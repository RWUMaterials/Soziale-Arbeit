import os
import sys
import requests
import discord

# Function to fetch file tree from GitHub
def get_github_file_tree(owner, repo, branch):
    url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch file tree from GitHub: {response.status_code}")
        return None

# Function to create Discord threads based on file tree
async def create_discord_threads(file_tree, channel):
    for item in file_tree['tree']:
        if item['type'] == 'tree':
            folder_name = item['path']
            folder_thread = await channel.create_thread(name=folder_name, auto_archive_duration=60)
            folder_content = ''
            for sub_item in file_tree['tree']:
                if sub_item['type'] == 'blob' and sub_item['path'].startswith(folder_name):
                    folder_content += f"- {sub_item['path'].split('/')[-1]}\n"
            if folder_content:
                await folder_thread.send(folder_content)

# Discord client
client = discord.Client()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Fetch repository details
    repo_details = os.getenv('GITHUB_REPOSITORY').split('/')
    GITHUB_OWNER = repo_details[0]
    GITHUB_REPO = repo_details[1]
    GITHUB_BRANCH = os.getenv('GITHUB_REF').split('/')[-1]

    # Fetch file tree from GitHub
    file_tree = get_github_file_tree(GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH)

    # Fetch the desired channel
    channel_id = 1224349080356917269  # Replace with your Discord channel ID
    channel = client.get_channel(channel_id)

    # Create Discord threads based on file tree
    await create_discord_threads(file_tree, channel)

# Run the Discord bot
client.run(sys.argv[1])
