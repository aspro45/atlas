# Atlas

AI-reviewed place records for a public map registry.

Atlas stores place submissions with sources, observations and review status. It is closer to a provenance registry than a simple map demo: the contract keeps who submitted a place, which sources back it, how GenLayer reviewed it and whether a challenge changed the final record.

## Public Surfaces

- App: https://tanawo3-atlas.vercel.app
- GitHub: https://github.com/aspro45/atlas
- Contract explorer: https://explorer-bradbury.genlayer.com/address/0x8D03b61859572d56372c80b00F9e36Ec00f60dBc

## Deployment Card

| Field | Value |
| --- | --- |
| Network | GenLayer Bradbury |
| Chain ID | 4221 |
| Contract | `0x8D03b61859572d56372c80b00F9e36Ec00f60dBc` |
| Deploy transaction | [`0x0cfdcda1...c39acd`](https://explorer-bradbury.genlayer.com/tx/0x47ac1bc4ce346f7068b8c89e6c75027031befa661ceca2f0b8a18f8584a65279) |
| Deployed | 2026-07-01T19:58:39.502Z |
| Contract file | `contracts/atlas_v2.py` |
| Source size | 38,006 bytes |

## Registry Model

Atlas works around place records:

- `set_atlas_standard` defines how locations should be reviewed.
- `create_place` stores the initial place claim.
- Source methods attach reference pages and observations.
- Review methods ask GenLayer to compare public evidence.
- Challenge and appeal methods preserve disagreement instead of overwriting it.

The frontend can read counts, recent places, category views, submitter views, source lists and full place records. That makes the UI useful for browsing the registry, not only submitting a form.

## Smoke Proof

| Method | Transaction |
| --- | --- |
| `set_atlas_standard` | [0x131be062...70a0e4](https://explorer-bradbury.genlayer.com/tx/0x131be0620c66f218befb65c032fd65ca38b7d617c145140fb427889eb470a0e4) |
| `create_place` | [0x3b189b39...bc844d](https://explorer-bradbury.genlayer.com/tx/0x3b189b39322c0e57f81e2480e106b19efaa9a990a904b9a33ee60724dbbc844d) |
| `add_source_wiki` | [0xd290a568...668805](https://explorer-bradbury.genlayer.com/tx/0xd290a568fbdb274fc1e7f459b6b8c14052f14265edbbba4ac5ceaf1df7668805) |
| `add_source_britannica` | [0xd5ae6a76...c88b11](https://explorer-bradbury.genlayer.com/tx/0xd5ae6a76113461a4aa45a598a60e5f9c38fa7e62c70fd5925bcad5ca88c88b11) |
| `add_observation` | [0x9889de60...94d586](https://explorer-bradbury.genlayer.com/tx/0x9889de6083865a0480ef6ef539c05d35c0c0c7cf4ebbb783ef8b1d1e3194d586) |
| `open_review` | [0x78155da0...986130](https://explorer-bradbury.genlayer.com/tx/0x78155da0dd653de87759a929c0c68f16fa92fe145b980967e085ccb283986130) |

## Running The App

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Security Boundary

This repo should stay publishable. Keep only public metadata, source code and static frontend files in Git. Do not commit keys, local vault data, `.env` files or Vercel project state.
