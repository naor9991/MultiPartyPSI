//
// Created by root on 7/25/16.
//

#ifndef MULTIPARTYPSI_POLYNOMIALFOLLOWER_H
#define MULTIPARTYPSI_POLYNOMIALFOLLOWER_H

#include "Follower.h"

#include <NTL/GF2E.h>
#include <NTL/GF2EX.h>
#include <NTL/GF2X.h>
#include <NTL/GF2XFactoring.h>
#include <NTL/vec_GF2E.h>
#include <NTL/ZZ.h>

NTL_CLIENT

class PolynomialFollower : public Follower {
public:
    PolynomialFollower(const FollowerSet& followerSet, const boost::shared_ptr<uint8_t> &secretShare, CSocket &leader);
    virtual ~PolynomialFollower() {};

    virtual void run();

private:
    void buildPolynomials();
    void generateIrreduciblePolynomial();

    vector<vector<uint8_t>> getPolynomialCoffBytes(NTL::GF2EX & polynomial);

    GF2X m_irreduciblePolynomial;
    vector<GF2EX> m_polynomials;

    uint32_t m_securityParameter;

    COPY_CTR(PolynomialFollower);
    ASSIGN_OP(PolynomialFollower);
};

#endif //MULTIPARTYPSI_POLYNOMIALFOLLOWER_H