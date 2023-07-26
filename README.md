**Disclaimer: Beta Version**

Welcome to the beta version of our client! This software is currently in the beta testing phase, which means it is not the final release version. As a beta version, it may still contain bugs, undergo frequent updates, and have limited features.
Important Points to Note:

**Use at Your Own Risk:** While we have made efforts to ensure the stability and reliability of the beta version, there is a possibility of encountering unexpected issues. Please use this software at your own risk.

**Limited Support:** As this is a beta release, our support resources may be focused on addressing critical bugs and gathering feedback from users. Therefore, support for beta versions may be limited compared to our stable releases.

**Feedback Appreciated:** Your feedback is invaluable to us. If you encounter any issues, have suggestions, or want to share your experiences with the beta version, please let us know. Your feedback will help us improve the software for the final release.

**Not for Production Use:** The beta version is intended for testing and evaluation purposes only. It is not recommended for use in a production environment where stability and reliability are crucial.
# DKG.py

**Python3 library for interaction with the OriginTrail Decentralized Knowledge Graph**

The official OriginTrail documentation for v6 can be found [here](https://docs.origintrail.io/dkg-v6-upcoming-version/introduction-to-dkg-v6-start-here).


## Intro - What is a Decentralized Knowledge Graph (DKG)


There are many available definitions of a knowledge graph, therefore we will present a simplified one focused on usability, rather than completeness. The purpose of this introduction is not to be a comprehensive guide for knowledge graphs, however it aims to get you started with the basics.

A **knowledge graph (KG)** is a network of entities — physical & digital objects, events or concepts — illustrating the relationship between them (aka a semantic network). KGs are used by major companies such as [Amazon](http://lunadong.com/talks/PG.pdf), [Google](https://en.wikipedia.org/wiki/Google_Knowledge_Graph), [Uber](https://www.youtube.com/watch?v=r3yMSl5NB_Q), [IBM](https://www.ibm.com/cloud/learn/knowledge-graph) etc for various applications: search, data integration, knowledge reasoning, recommendation engines, analytics, machine learning and AI etc.

Key characteristics of knowledge graphs:
* focus on data connections as "first class citizens" (linked data)
* designed to ingest data from multiple sources, usually in different formats
* flexible data model, easily extendable

Common knowledge graphs however are deployed within the domain of one organization and are designed to capture knowledge from various sources both from within and outside of the organization.

We define **decentralized knowledge graph (DKG)** as a global shared knowledge graph that is designed to benefit organizations and individuals by providing a common infrastructure for data exchange. The DKG:

* Enables Dapps with search, integration, analytics, AI and ML capabilities for any data source: blockchains, IPFS, enterprise systems, web services, personal devices
* Removes central authorities (decentralized infrastructure)
* Enables permissionless PUBLISH and QUERY (public network)
* Decentralized identity & Verifiable Credentials based access control (references private data)







## Install & run

### Required versions

* python `3.11.4`
* poetry `1.5.1`

### Setup environment

Create virtual environment (you can choose any existing folder this command will create configurations and virtual env for python):
```bash
python3 -m venv /path/to/folder
```

Inside of previously generated folder you will find activate script in bin folder and run it:
```bash
source /path/to/folder/bin/activate
```

Install dependencies:
```bash
poetry install
```

### Run

Run demo example file: 
```bash
python3 demo.py
```

## The OriginTrail DKG Architecture

The OriginTrail Decentralized Network implements the DKG according to the OriginTrail protocol.

It is:

* **a permissionless network** - anyone can run OriginTrail nodes
* **a multi-chain data exchange network** - connects to several blockchains (currently Ethereum and xDai with more integrations upcoming such as with Polkadot)
* **designed for off-chain data exchange using standardized data models** (GS1 & W3C standards and recommendations)
* **public open source software**
* **infrastructure for knowledge marketplaces & tenders** - more info [here](https://www.youtube.com/watch?v=4uCxYGRh5fk)

More information is available on the OriginTrail [website](https://origintrail.io), [official documentation](https://docs.origintrail.io) and [blog](https://medium.com/origintrail).


![](https://i.imgur.com/yTNtZE1.png)


## DKG Client library

This library provides an interface into the OriginTrail Decentralized Knowledge Graph, enabling:

* creating & updating assets on the public DKG
* network and local querying of information based on topics and identifiers
* verifying the integrity of queried data

### Documentation & Usage

Start here: [official DKGv6 documentation](https://docs.origintrail.io/dkg-v6-beta/introduction-to-dkg-v6-start-here)

## Learn more

More information can be found on the [official DKGv6 documentation](https://docs.origintrail.io/dkg-v6-upcoming-version/introduction-to-dkg-v6-start-here), [website](https://origintrail.io) and [Github](https://github.com/OriginTrail).

## Get in touch

Get in touch with the OriginTrail tech community through [Discord](https://discordapp.com/invite/FCgYk2S).

[`#traceon`]()