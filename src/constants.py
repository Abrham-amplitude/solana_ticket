from solana.publickey import PublicKey

# Network URLs
DEVNET_URL = "https://api.devnet.solana.com"
TESTNET_URL = "https://api.testnet.solana.com"
MAINNET_URL = "https://api.mainnet-beta.solana.com"

# Program IDs (you'll need to update these after deployment)
TICKET_PROGRAM_ID = PublicKey("YOUR_PROGRAM_ID_HERE")

# Constants for ticket data
TICKET_SPACE = 49  # 8 + 8 + 32 + 1 bytes 