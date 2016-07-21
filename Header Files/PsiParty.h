//
// Created by root on 6/20/16.
//

#ifndef LIBSCAPI_PSIPARTY_H
#define LIBSCAPI_PSIPARTY_H

#include "MultiPartyPlayer.h"
#include "statistics.h"
#include "../PSI/src/util/typedefs.h"
#include "../PSI/src/util/crypto/crypto.h"

class PsiParty : public MultiPartyPlayer {
public:
    PsiParty(uint partyId, ConfigFile &config, boost::asio::io_service &ioService);
    virtual ~PsiParty() {
        if(m_elementSizeInBits > m_maskbitlen)
            free(m_eleptr);
    };

    void run();

    static void printHex(const uint8_t *arr, uint32_t size);
    void printShares(const uint8_t *arr, uint32_t numOfShares);
private:

    /**
     * Works as follows:
     * randomly pick $numberOfParties$-1 random shares with size $ElementSize$ and send them to all the parties
     * receive $numberOfParties$-1 shares from all the parties with size $ElementSize$
     * compute PRG on each of the shares with expansion factor of $SetSize$ and XOR them all.
     */
    void additiveSecretShare();

    void runAsLeader();
    void runAsFollower(CSocket *leader);
    void finishAndReportStatsToServer();
    void syncronize();

    crypto* initializeCrypto(uint8_t* seed_buf);
    void runLeaderAgainstFollower(std::pair<uint32_t, CSocket*> party, uint8_t **leaderResults,
                                  uint32_t* nelesinbin, uint32_t outbitlen, uint8_t * const hash_table);

    uint32_t getMaskSizeInBytes() {
        return ceil_divide(m_maskbitlen, 8);
    }

    void LoadConfiguration();

    const double EPSILON=1.2;
    COPY_CTR(PsiParty);
    ASSIGN_OP(PsiParty);

    uint32_t m_setSize;
    uint32_t m_elementSizeInBits;
    byte *m_secretShare;
    uint8_t *m_elements;
    crypto* m_crypt;
    uint32_t m_maskbitlen;
    struct statistics m_statistics;
    enum Strategy m_strategy;
    uint32_t m_numOfBins;
    prf_state_ctx m_prfState;

    uint32_t m_symsecbits;

    uint8_t* m_eleptr;

    uint32_t m_internal_bitlen;
    uint32_t m_seedSize;
};

#endif //LIBSCAPI_PSIPARTY_H
