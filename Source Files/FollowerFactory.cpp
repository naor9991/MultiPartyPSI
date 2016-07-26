//
// Created by root on 7/21/16.
//

#include "FollowerFactory.h"
#include "NaiveFollower.h"
#include "GBFFollower.h"
#include "PolynomialFollower.h"
#include "SimpleHashingPolynomialFollower.h"

boost::shared_ptr<Follower> FollowerFactory::getFollower(enum Strategy strategy, const FollowerSet& followerSet, const boost::shared_ptr<uint8_t> &secretShare,
                                                         CSocket &leader, uint32_t maxBinSize) {
    switch(strategy) {
        case Strategy::NAIVE_METHOD_SMALL_N:
            return boost::shared_ptr<Follower>(new NaiveFollower(followerSet, secretShare, leader));
        case Strategy::BLOOM_FILTER:
            return boost::shared_ptr<Follower>(new GBFFollower(followerSet, secretShare, leader));
        case Strategy::POLYNOMIALS:
            return boost::shared_ptr<Follower>(new PolynomialFollower(followerSet, secretShare, leader));
        case Strategy::POLYNOMIALS_SIMPLE_HASH:
            return boost::shared_ptr<Follower>(new SimpleHashingPolynomialFollower(followerSet, secretShare, leader, maxBinSize));
        default:
            break;
    }
    throw(system_error());
}