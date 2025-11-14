# Environment Setup

## Creating .env File

Create a `.env` file in the project root with your OpenAI API key:

```bash
# In WSL terminal
cd /mnt/c/Users/avish/OneDrive/Desktop/User\ Story\ automation\ frontend/user-story-automation

# Create .env file
echo "auth_key=your_openai_api_key_here" > .env
```

Or manually create `.env` with:
```
auth_key=your_openai_api_key_here
```

**Note:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Alternative Environment Variable

You can also use `OPENAI_API_KEY` instead of `auth_key`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Security

- Never commit `.env` file to Git (it's in `.gitignore`)
- Keep your API key secure
- Don't share your API key publicly

