<a name="readme-top"></a>

___

<br />
<div align="center">
  <a href="https://github.com/OriginTrail/dkg.py">
    <img src="images/banner.jpg" alt="Python SDK Banner">
  </a>

  <h3 align="center"><b>dkg.py</b></h3>

  <p align="center">
    Python SDK for interacting with the OriginTrail Decentralized Knowledge Graph
    </br>
    <a href="https://docs.origintrail.io/">OriginTrail Docs</a>
    ·
    <a href="https://github.com/OriginTrail/dkg.py/examples/demo.py">View Demo</a>
    ·
    <a href="https://github.com/OriginTrail/dkg.py/issues">Report Bug</a>
    ·
    <a href="https://github.com/OriginTrail/dkg.py/issues">Request Feature</a>
  </p>
</div>

</br>

> **Disclaimer: Beta Version**
>
> Welcome to the beta version of our client! This software is currently in the beta testing phase, which means it is not the final release version. As a beta version, it may still contain bugs, undergo frequent updates, and have limited features.
Important Points to Note:

> **Use at Your Own Risk:** While we have made efforts to ensure the stability and reliability of the beta version, there is a possibility of encountering unexpected issues. Please use this software at your own risk.

> **Limited Support:** As this is a beta release, our support resources may be focused on addressing critical bugs and gathering feedback from users. Therefore, support for beta versions may be limited compared to our stable releases.

> **Feedback Appreciated:** Your feedback is invaluable to us. If you encounter any issues, have suggestions, or want to share your experiences with the beta version, please let us know. Your feedback will help us improve the software for the final release.

> **Not for Production Use:** The beta version is intended for testing and evaluation purposes only. It is not recommended for use in a production environment where stability and reliability are crucial.

</br>

<details open>
  <summary>
    <b>Table of Contents</b>
  </summary>
  <ol>
    <li>
      <a href="#📚-about-the-project">📚 About The Project</a>
      <ul>
        <li><a href="#what-is-the-decentralized-knowledge-graph">What is the Decentralized Knowledge Graph?</a></li>
        <li><a href="#the-origintrail-dkg-architecture">The OriginTrail DKG Architecture</a></li>
        <li><a href="#what-is-a-knowledge-asset">What is a Knowledge Asset?</a></li>
      </ul>
    </li>
    <li>
      <a href="#🚀-getting-started">🚀 Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
      <a href="#📜-roadmap">📜 Roadmap</a>
      <ul>
        <li><a href="#1️⃣-pre-development-phase">1️⃣ Pre-development Phase</a></li>
        <li><a href="#2️⃣-development-phase">2️⃣ Development Phase</a></li>
        <li><a href="#3️⃣-documentation-phase">3️⃣ Documentation Phase</a></li>
        <li><a href="#4️⃣-pre-release-phase">4️⃣ Pre-release Phase</a></li>
        <li><a href="#5️⃣-release">5️⃣ Release</a></li>
        <li><a href="#6️⃣-post-release">6️⃣ Post-release</a></li>
      </ul>
    </li>
    <li><a href="#📄-license">📄 License</a></li>
    <li><a href="#🤝-contributing">🤝 Contributing</a></li>
    <li><a href="#❤️-thanks-to-all-contributors">❤️ Contributors</a></li>
    <li><a href="#🌟-acknowledgements">🌟 Acknowledgements</a></li>
    <li><a href="#📰-social-media">📰 Social Media</a></li>
  </ol>
</details>

___

<br/>

## 📚 About The Project

<details open>
<summary>

### **What is the Decentralized Knowledge Graph?**
</summary>

<br/>

<div align="center">
    <img src="images/nodes.png" alt="Knowledge Asset" width="200">
</div>

OriginTrail Decentralized Knowledge Graph (DKG), hosted on the OriginTrail Decentralized Network (ODN) as trusted knowledge infrastructure, is shared global Knowledge Graph of Knowledge Assets. Running on the basis of the permissionless multi-chain OriginTrail protocol, it combines blockchains and knowledge graph technology to enable trusted AI applications based on key W3C standards.
</details>

<details open>
<summary>

### **The OriginTrail DKG Architecture**
</summary>

<br/>

The OriginTrail tech stack is a three layer structure, consisting of the multi-chain consensus layer (OriginTrail layer 1, running on multiple blockchains), the Decentralized Knowledge Graph layer (OriginTrail Layer 2, hosted on the ODN) and Trusted Knowledge applications in the application layer. 

<div align="center">
    <img src="images/dkg-architecture.png" alt="DKG Architecture" width="400">
</div>

Further, the architecture differentiates between **the public, replicated knowledge graph** shared by all network nodes according to the protocol, and **private Knowledge graphs** hosted separately by each of the OriginTrail nodes.

**Anyone can run an OriginTrail node and become part of the ODN, contributing  to the network capacity and hosting the OriginTrail DKG. The OriginTrail node is the ultimate data service for data and knowledge intensive Web3 applications and is used as the key backbone for trusted AI applications (see https://chatdkg.ai)**
</details>

<details open>
<summary>

### **What is a Knowledge Asset?**
</summary>

<br/>

<div align="center">
    <img src="images/ka.png" alt="Knowledge Asset" width="200">
</div>

**Knowledge Asset is the new, AI‑ready resource for the Internet**

Knowledge Assets are verifiable containers of structured knowledge that live on the OriginTrail DKG and provide:
- **Discoverability - UAL is the new URL**. Uniform Asset Locators (UALs, based on the W3C Decentralized Identifiers) are a new Web3 knowledge identifier (extensions of the Uniform Resource Locators - URLs) which identify a specific piece of knowledge and make it easy to find and connect with other Knowledge Assets.
- **Ownership - NFTs enable ownership**. Each Knowledge Asset contains an NFT token that enables ownership, knowledge asset administration and market mechanisms.
- **Verifiability - On-chain information origin and verifiable trail**. The blockchain tech increases trust, security, transparency, and the traceability of information.


By their nature, Knowledge Assets are semantic resources (following the W3C Semantic Web set of standards), and through their symbolic representations inherently AI ready. See more at https://chatdkg.ai
<br/>

**Discover Knowledge Assets with the DKG Explorer:**
<div align="center">
    <table>
        <tr>
            <td align="center">
                <a href="https://dkg.origintrail.io/explore?ual=did:dkg:otp/0x5cac41237127f94c2d21dae0b14bfefa99880630/309100">
                  <img src="images/knowledge-assets-graph1.svg" width="300" alt="Knowledge Assets Graph 1">
                </a>
                <br><b>Supply Chains</b>
            </td>
            <td align="center">
                <a href="https://dkg.origintrail.io/explore?ual=did:dkg:otp/0x5cac41237127f94c2d21dae0b14bfefa99880630/309285">
                  <img src="images/knowledge-assets-graph2.svg" width="300" alt="Knowledge Assets Graph 2">
                </a>
                <br><b>Construction</b>
            </td>
            <td align="center">
                <a href="https://dkg.origintrail.io/explore?ual=did:dkg:otp/0x5cac41237127f94c2d21dae0b14bfefa99880630/309222">
                  <img src="images/knowledge-assets-graph3.svg" width="300" alt="Knowledge Assets Graph 3">
                </a>
                <br><b>Life sciences and healthcare</b>
            </td>
            <td align="center">
                <a href="https://dkg.origintrail.io/explore?ual=did:dkg:otp/0x5cac41237127f94c2d21dae0b14bfefa99880630/308028">
                  <img src="images/knowledge-assets-graph4.svg" width="300" alt="Knowledge Assets Graph 3">
                </a>
                <br><b>Metaverse</b>
            </td>
        </tr>
    </table>
</div>


</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
<br/>

## 🚀 Getting Started

___

### Prerequisites

* python `>=3.10`
* poetry `>=1.5.1`


In order to use in the local environment, make sure to [run the local DKG network](https://github.com/OriginTrail/ot-node?tab=readme-ov-file#local-network-setup).

___
<br/>

### Installation


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

Now you can run a demo example file (you need to have the local DKG network running):
```bash
python3 examples/demo.py
```

<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📜 Roadmap

This roadmap outlines the goals for the first major release of the `dkg.py`. Each section represents a stage in the development process and the features we plan to implement.

<details open>
<summary>

### 1️⃣ Pre-development Phase

</summary>

- [x] **Requirement Analysis and Planning**
  - [x] Define the project's scope
  - [x] Identify the core functionalities

- [x] **Design**
  - [x] Plan the library's architecture
  - [x] Establish coding standards

- [ ] **Setup Development Environment**
  - [x] Setup development, testing and production environments
  - [ ] Add pytest config
  - [ ] Add mypy config
  - [ ] Add tox config ?
  - [ ] Setup Continuous Integration (CI) and Continuous Deployment (CD) pipeline
</details>

<details open>
<summary>

### 2️⃣ Development Phase
</summary>

| Feature | Status | Tests coverage |
|:-:|:-:|:-:|
| Get Allowance | 🟩 Completed | ❌ |
| Set Allowance | 🟩 Completed | ❌ |
| Increase Allowance | 🟩 Completed | ❌ |
| Decrease Allowance | 🟩 Completed | ❌ |
| Get Bid Suggestion | 🟩 Completed | ❌ |
| Create | 🟩 Completed | ❌ |
| Transfer | 🟩 Completed | ❌ |
| Update | 🟩 Completed | ❌ |
| Wait for finalization | 🟥 Not Started | ❌ |
| Cancel update | 🟩 Completed | ❌ |
| Burn | 🟩 Completed | ❌ |
| Get | 🟩 Completed | ❌ |
| Query | 🟩 Completed | ❌ |
| Extend storing period | 🟩 Completed | ❌ |
| Add tokens | 🟩 Completed | ❌ |
| Add update tokens | 🟩 Completed | ❌ |
| Get owner | 🟩 Completed | ❌ |
| Experimental | 🟥 Not Started | ❌ |
</details>

<details open>
<summary>

### 3️⃣ Documentation Phase
</summary>

- [ ] Write comprehensive documentation
- [x] Provide examples and use-cases
- [ ] Review and finalize documentation
</details>

<details open>
<summary>

### 4️⃣ Pre-release Phase
</summary>

- [ ] **Beta Release**
  - [X] Release a beta version for testing
  - [ ] Gather and address feedback

- **Bug Fixes**
  - Identify and fix bugs

- [ ] **Final Testing and QA**
  - [ ] Perform comprehensive testing
  - [ ] Ensure the library meets quality standards
</details>

<details open>
<summary>

### 5️⃣ Release
</summary>

- [ ] Merge the first version into the main branch
- [ ] Release the v1.0.0 of the `dkg.py` library
</details>

<details open>
<summary>

### 6️⃣ Post-release
</summary>

- Monitor for any issues
- Plan for next versions based on user feedback and usage
</details>

<br/>

**Note:** This roadmap is subject to changes. Each step will be accompanied by appropriate documentation, testing and code review to maintain the quality of the library.

<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📄 License

Distributed under the Apache-2.0 License. See `LICENSE` file for more information.

<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ❤️ Thanks to all Contributors!

<!-- readme: <u.hubar>,collaborators,<mucke12>,contributors/- -start -->
<!-- readme: <u.hubar>,collaborators,<mucke12>,contributors/- -end -->

<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🌟 Acknowledgements

- [web3.py](https://github.com/ethereum/web3.py): Basis for this project


<br/>
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📰 Social Media

<br/>

<div align="center">
  <a href="https://medium.com/origintrail">
    <img src="images/icons/medium.svg" alt="Medium Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://t.me/origintrail">
    <img src="images/icons/telegram.svg" alt="Telegram Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://x.com/origin_trail">
    <img src="images/icons/x.svg" alt="X Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://www.youtube.com/c/origintrail">
    <img src="images/icons/youtube.svg" alt="YouTube Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://www.linkedin.com/company/origintrail/">
    <img src="images/icons/linkedin.svg" alt="LinkedIn Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://discord.gg/cCRPzzmnNT">
    <img src="images/icons/discord.svg" alt="Discord Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://www.reddit.com/r/OriginTrail/">
    <img src="images/icons/reddit.svg" alt="Reddit Badge" width="30" style="margin-right: 10px"/>
  </a>
  <a href="https://coinmarketcap.com/currencies/origintrail/">
    <img src="images/icons/coinmarketcap.svg" alt="Coinmarketcap Badge" width="30" style="margin-right: 10px"/>
  </a>
</div>

___
