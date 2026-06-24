# Security

Atlas is a public static frontend connected to a public GenLayer Studionet contract. The repository must stay free of wallet secrets and local automation material.

## Do Not Commit

- private keys
- seed phrases or mnemonics
- vault files
- `.env` or `.env.local`
- faucet logs
- dashboard exports containing wallet metadata

The contract address, deployer address, explorer URLs, and smoke transaction hashes are public chain metadata.

## Runtime Model

The app is static HTML, CSS, and browser JavaScript. Reads use the public GenLayer Studionet RPC through the shared `genlayer-lite.js` helper. Writes are only sent after the visitor connects an injected EVM wallet and confirms the transaction.

No server route stores wallet data. No Vercel secret is required for production.

## Production Headers

`vercel.json` applies HSTS, frame blocking, MIME sniffing protection, a strict referrer policy, and a restrictive permissions policy.

## Reporting

Use a private GitHub security advisory for sensitive issues. Do not publish exploit details in a public issue before a fix exists.
