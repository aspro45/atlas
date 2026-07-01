# Atlas

AI-reviewed place records for a public map registry.

Atlas stores place submissions with sources, observations and review status. It is closer to a provenance registry than a simple map demo: the contract keeps who submitted a place, which sources back it, how GenLayer reviewed it and whether a challenge changed the final record.

## Public Surfaces

- App: https://atlas-github-ten.vercel.app
- GitHub: https://github.com/aspro45/atlas
- Contract explorer: https://explorer-studio.genlayer.com/contracts/0x4F611050934677D94940c2998aF336EE9BEf9023

## Deployment Card

| Field | Value |
| --- | --- |
| Network | GenLayer Studionet |
| Chain ID | 61999 |
| Contract | `0x4F611050934677D94940c2998aF336EE9BEf9023` |
| Deploy transaction | [`0x0cfdcda1...c39acd`](https://explorer-studio.genlayer.com/tx/0x0cfdcda1779cace53323d26e69c7e80ae66ceede479d1447863f272544c39acd) |
| Deployed | 2026-06-23T16:31:49.455Z |
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
| `set_atlas_standard` | [0xe885c0b3...8e05a4](https://explorer-studio.genlayer.com/tx/0xe885c0b3a7f084ceda35bb7935339fd8bed61dec3eb4297fd625a9369c8e05a4) |
| `create_place` | [0x22b557eb...39186b](https://explorer-studio.genlayer.com/tx/0x22b557eba74cfda4d3dd0a2fbae1de6465c46942aa650ddcd545e8237539186b) |
| `add_source_wiki` | [0x09ed0658...f566ba](https://explorer-studio.genlayer.com/tx/0x09ed0658cbb3e8b4a1654755c87c99c10e6be3411d1cbc48c2c97a89d0f566ba) |
| `add_source_britannica` | [0xa552ba69...bcada1](https://explorer-studio.genlayer.com/tx/0xa552ba694901b12862fdeb279e4fd7f44d8b2238c7e0acb27fbb05f368bcada1) |
| `add_observation` | [0x2fa41f61...ef9ad7](https://explorer-studio.genlayer.com/tx/0x2fa41f61936722ba4e5619240cf1a8a27ad5b9e4665a5bd4bbf8d20d03ef9ad7) |
| `open_review` | [0xea04568c...688550](https://explorer-studio.genlayer.com/tx/0xea04568c6894737ef1ec31c1cd2200a344f415e89a50df68bde874684d688550) |

## Running The App

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Security Boundary

This repo should stay publishable. Keep only public metadata, source code and static frontend files in Git. Do not commit keys, local vault data, `.env` files or Vercel project state.
