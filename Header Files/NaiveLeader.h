//
// Created by root on 7/21/16.
//

#ifndef MULTIPARTYPSI_NAIVELEADER_H
#define MULTIPARTYPSI_NAIVELEADER_H

#include "Leader.h"

class NaiveLeader : public Leader {
public:
    NaiveLeader(const map<uint32_t , uint8_t *> &leaderResults, const boost::shared_ptr<uint32_t> &bin_ids, const boost::shared_ptr<uint32_t> &perm, uint32_t numOfBins,
        const boost::shared_ptr<uint8_t> &secretShare, uint32_t maskSizeInBytes, uint32_t setSize, std::map<uint32_t, CSocket*> parties,
        uint32_t numOfHashFunctions) :
            Leader(leaderResults, bin_ids, perm, numOfBins, secretShare, maskSizeInBytes, setSize, parties, numOfHashFunctions) {
    };
    virtual ~NaiveLeader() {};

    virtual vector<uint32_t> run();
private:
    COPY_CTR(NaiveLeader);
    ASSIGN_OP(NaiveLeader);

    void receiveServerMasks();

    bool isElementInAllSets(uint32_t index);

    bool isZeroXOR(uint8_t *formerShare, uint32_t partyNum);
};


#endif //MULTIPARTYPSI_NAIVELEADER_H
