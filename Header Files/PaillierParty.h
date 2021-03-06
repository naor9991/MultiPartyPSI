//
// Created by root on 8/1/16.
//

#ifndef MULTIPARTYPSI_PAILLIER_H
#define MULTIPARTYPSI_PAILLIER_H

#include "MultiPartyPlayer.h"
#include "BaseMPSIParty.h"
#include <NTL/ZZ.h>

NTL_CLIENT

class PaillierParty : public BaseMPSIParty {
public:
    PaillierParty(uint32_t partyId, ConfigFile &config, boost::asio::io_service &ioService);

protected:
    ZZ encrypt(const ZZ& plain);
    ZZ partialDecrypt(const ZZ& cipher);
    ZZ decrypt(const std::map<uint32_t,ZZ> &partialCiphers,
               const std::vector<ZZ> &pubKeys);
    ZZ getPubKey() {
        return m_pubKey;
    }
    static void sendZZTo(const ZZ& element, const boost::shared_ptr<CSocket> &socket);
    static void receiveZZFrom(ZZ& element, const boost::shared_ptr<CSocket> &socket);
    static ZZ getRandomInNStar(const ZZ& mod);
protected:
    COPY_CTR(PaillierParty);
    ASSIGN_OP(PaillierParty);

    void initPaiilier();
    void secretShare();
    uint32_t factorial(uint32_t n);
    ZZ L_function(const ZZ& value);


    ZZ m_pTag;
    ZZ m_qTag;
    ZZ m_p;
    ZZ m_q;
    ZZ m_n;
    ZZ m_m;
    ZZ m_field;
    ZZ m_share;
    uint32_t m_delta;
    ZZ m_a;
    ZZ m_b;
    ZZ m_g;
    ZZ m_pubKey;
    std::map<uint32_t, ZZ> m_lagrangeBasis;
};


#endif //MULTIPARTYPSI_PAILLIER_H
