//
// Created by root on 7/21/16.
//

#include "NaiveLeader.h"
#include "defs.h"
#include "ot-psi.h"

void *NaiveLeader::receiveMasks(void *ctx_tmp) {
    mask_rcv_ctx* ctx = (mask_rcv_ctx*) ctx_tmp;
    ctx->sock->Receive(ctx->rcv_buf, ctx->maskbytelen * ctx->nmasks);
}

void NaiveLeader::receiveServerData() {
    vector<pthread_t> rcv_masks_threads;

    boost::shared_ptr<mask_rcv_ctx> rcv_ctxs(new mask_rcv_ctx[m_parties.size()+1]);
    for (auto &party : m_parties) {
        pthread_t rcv_masks_thread;

        //receive server masks
        m_partiesResults[party.first] = boost::shared_ptr<uint8_t>(new uint8_t[NUM_HASH_FUNCTIONS * m_setSize * m_maskSizeInBytes]);

        //receive_masks(server_masks, NUM_HASH_FUNCTIONS * neles, maskbytelen, sock[0]);
        //use a separate thread to receive the server's masks
        (rcv_ctxs.get())[party.first - 1].rcv_buf = m_partiesResults[party.first].get();
        (rcv_ctxs.get())[party.first - 1].nmasks = NUM_HASH_FUNCTIONS * m_setSize;
        (rcv_ctxs.get())[party.first - 1].maskbytelen = m_maskSizeInBytes;
        (rcv_ctxs.get())[party.first - 1].sock = party.second.get();
        if(pthread_create(&rcv_masks_thread, NULL, NaiveLeader::receiveMasks, (void*) (&(rcv_ctxs.get())[party.first - 1]))) {
            cerr << "Error in creating new pthread at cuckoo hashing!" << endl;
            exit(0);
        }

        rcv_masks_threads.push_back(rcv_masks_thread);
    }

    for (auto rcv_masks_thread : rcv_masks_threads) {
        //meanwhile generate the hash table
        //GHashTable* map = otpsi_create_hash_table(ceil_divide(inbitlen,8), masks, neles, maskbytelen, perm);
        //intersect_size = otpsi_find_intersection(eleptr, result, ceil_divide(inbitlen,8), masks, neles, server_masks,
        //		neles * NUM_HASH_FUNCTIONS, maskbytelen, perm);
        //wait for receiving thread
        if(pthread_join(rcv_masks_thread, NULL)) {
            cerr << "Error in joining pthread at cuckoo hashing!" << endl;
            exit(0);
        }
    }
}

bool NaiveLeader::isElementInAllSets(uint32_t index) {

    uint32_t binIndex = m_hashInfo.get()[index].binIndex;

    uint32_t newIndex = m_hashInfo.get()[index].tableIndex;

    uint8_t* secret = &(m_secretShare.get()[binIndex*m_maskSizeInBytes]);

    for (auto &party : m_parties) {
        XOR(secret, m_leaderResults[party.first].get()+newIndex*m_maskSizeInBytes, m_maskSizeInBytes);
    }

    // 1 is always the leader Id
    return isZeroXOR(secret,2);
}

bool NaiveLeader::isZeroXOR(uint8_t *formerShare, uint32_t partyNum) {
    if (partyNum <= m_parties.size()+1) {
        uint8_t *partyResult = m_partiesResults[partyNum].get();
        for (uint32_t i = 0; i < m_setSize *m_numOfHashFunctions; i++) {
            XOR(formerShare,partyResult+i*m_maskSizeInBytes, m_maskSizeInBytes);
            if (isZeroXOR(formerShare,partyNum+1)) {
                return true;
            }
            XOR(formerShare,partyResult+i*m_maskSizeInBytes, m_maskSizeInBytes);
        }
        return false;
    }

    for (uint32_t i = 0; i < m_maskSizeInBytes; i++) {
        if (formerShare[i] != 0) {
            return false;
        }
    }
    return true;
};