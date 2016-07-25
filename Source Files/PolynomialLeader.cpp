//
// Created by root on 7/25/16.
//

#include "PolynomialLeader.h"
#include "PolynomialUtils.h"
#include <vector>
#include <NTL/GF2EX.h>
#include <NTL/GF2XFactoring.h>

PolynomialLeader::PolynomialLeader(const map <uint32_t, boost::shared_ptr<uint8_t>> &leaderResults,
                 const boost::shared_ptr <uint32_t> &bin_ids, const boost::shared_ptr <uint32_t> &perm, uint32_t numOfBins,
                 const boost::shared_ptr <uint8_t> &secretShare, uint32_t maskSizeInBytes, uint32_t setSize,
                 boost::shared_ptr<uint8_t> elements, uint32_t elementSize, const boost::shared_ptr<uint32_t> &hashed_by,
                 const std::map <uint32_t, boost::shared_ptr<CSocket>> &parties, uint32_t numOfHashFunctions) :
        Leader(leaderResults,bin_ids,perm,numOfBins,secretShare,maskSizeInBytes,setSize,elements,
               elementSize,hashed_by,parties,numOfHashFunctions) {

    uint32_t securityParameter = maskSizeInBytes*8;
    GF2X irreduciblePolynomial = BuildSparseIrred_GF2X(securityParameter);
    GF2E::init(irreduciblePolynomial);

}

std::vector<uint32_t> PolynomialLeader::run() {

    receiveAllPolynomials();

    vector<uint32_t> intersection;

    for (uint32_t i = 0; i < m_setSize; i++) {
        if (isElementInAllSets(i)) {
            intersection.push_back(i);
        }
    }

    return intersection;
}

void PolynomialLeader::receiveAllPolynomials() {

    vector<pthread_t> rcv_polynomials_threads;

    boost::shared_ptr<polynomial_rcv_ctx> rcv_ctxs(new polynomial_rcv_ctx[m_parties.size()+1]);
    for (auto &party : m_parties) {
        pthread_t rcv_polynomial_thread;

        //receive_masks(server_masks, NUM_HASH_FUNCTIONS * neles, maskbytelen, sock[0]);
        //use a separate thread to receive the server's masks
        (rcv_ctxs.get())[party.first - 1].polynoms = new NTL::GF2EX*[m_numOfHashFunctions];

        (rcv_ctxs.get())[party.first - 1].setSize = m_setSize;
        (rcv_ctxs.get())[party.first - 1].numOfHashFunction = m_numOfHashFunctions;
        (rcv_ctxs.get())[party.first - 1].maskbytelen = m_maskSizeInBytes;
        (rcv_ctxs.get())[party.first - 1].sock = party.second.get();


        if(pthread_create(&rcv_polynomial_thread, NULL, PolynomialLeader::receivePolynomials, (void*) (&(rcv_ctxs.get()[party.first - 1])))) {
            cerr << "Error in creating new pthread at cuckoo hashing!" << endl;
            exit(0);
        }

        rcv_polynomials_threads.push_back(rcv_polynomial_thread);
    }

    for (auto &rcv_filters_thread : rcv_polynomials_threads) {
        //meanwhile generate the hash table
        //GHashTable* map = otpsi_create_hash_table(ceil_divide(inbitlen,8), masks, neles, maskbytelen, perm);
        //intersect_size = otpsi_find_intersection(eleptr, result, ceil_divide(inbitlen,8), masks, neles, server_masks,
        //		neles * NUM_HASH_FUNCTIONS, maskbytelen, perm);
        //wait for receiving thread
        if(pthread_join(rcv_filters_thread, NULL)) {
            cerr << "Error in joining pthread at cuckoo hashing!" << endl;
            exit(0);
        }
    }

    for (auto &party : m_parties) {
        m_partiesPolynomials[party.first] = std::vector<boost::shared_ptr<GF2EX>>();
        NTL::GF2EX** polynoms = (rcv_ctxs.get())[party.first - 1].polynoms;
        for (uint32_t i=0; i < m_numOfHashFunctions; i++) {
            m_partiesPolynomials[party.first].push_back(boost::shared_ptr<GF2EX>(polynoms[i]));
        }
    }
}

bool PolynomialLeader::isElementInAllSets(uint32_t index) {

    uint32_t binIndex = getBinIndex(index);

    uint32_t newIndex = getIndexInHashTable(index);

    uint8_t* secret = &(m_secretShare.get()[binIndex*m_maskSizeInBytes]);

    uint32_t hash_index = m_hashedBy.get()[binIndex];

    for (auto &party : m_parties) {
        XOR(secret, m_leaderResults[party.first].get()+newIndex*m_maskSizeInBytes, m_maskSizeInBytes);

        NTL::GF2E element = PolynomialUtils::convertBytesToGF2E(m_elements.get()+index*m_elementSize,m_elementSize);
        GF2E value = eval(*(m_partiesPolynomials[party.first][hash_index].get()),element);
        vector<uint8_t> arr = PolynomialUtils::convertElementToBytes(value);

        XOR(secret, arr.data(), m_maskSizeInBytes);
    }

    // 1 is always the leader Id
    for (uint32_t i = 0; i < m_maskSizeInBytes; i++) {
        if (secret[i] != 0) {
            return false;
        }
    }
    return true;
}

void *PolynomialLeader::receivePolynomials(void *ctx_tmp) {

    polynomial_rcv_ctx* ctx = (polynomial_rcv_ctx*) ctx_tmp;

    uint32_t coefficientSize = ctx->maskbytelen;

    for (uint32_t i = 0; i < ctx->numOfHashFunction; i++) {
        ctx->polynoms[i] = new NTL::GF2EX();
        for (uint32_t j=0; j < ctx->setSize; j++) {
            vector<uint8_t> coefficient(coefficientSize);
            ctx->sock->Receive(coefficient.data(), coefficientSize);
            NTL::GF2E coeffElement = PolynomialUtils::convertBytesToGF2E(coefficient.data(), coefficientSize);
            SetCoeff(*ctx->polynoms[i], j, coeffElement);
        }
    }
}