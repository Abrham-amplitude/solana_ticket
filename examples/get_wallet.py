from solders.keypair import Keypair

# Create a new wallet
wallet = Keypair()

# Print the public key (wallet address)
print("\nYour wallet address is:")
print(wallet.pubkey())
print("\nTo airdrop SOL, run this command:")
print(f"solana airdrop 2 {wallet.pubkey()} --url devnet\n")

# Save the private key (optional)
print("Your private key (save this somewhere safe):")
print(bytes(wallet.secret_key).hex()) 