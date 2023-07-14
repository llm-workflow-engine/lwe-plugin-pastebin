# LLM Workflow Engine (LWE) Pastebin plugin

Pastebin plugin for [LLM Workflow Engine](https://github.com/llm-workflow-engine/llm-workflow-engine)

Post a conversation to [https://pastebin.com](https://pastebin.com)

## Installation

Grab your API developer key from [https://pastebin.com/doc_api](https://pastebin.com/doc_api) -- you'll need to have a
user account on [https://pastebin.com](https://pastebin.com) and be logged in to see your developer key there.

Export the key into your local environment:

```bash
export PASTEBIN_API_DEVELOPER_KEY=<API_KEY>
```

If you want to paste as a specific user, you'll need to generate an `api_user_key`, instructions can be found [here](https://pastebin.com/doc_api#9)

Then export the key into your local environment:

```bash
export PASTEBIN_API_USER_KEY=<API_KEY>
```

### From packages

Install the latest version of this software directly from github with pip:

```bash
pip install git+https://github.com/llm-workflow-engine/lwe-plugin-pastebin
```

### From source (recommended for development)

Install the latest version of this software directly from git:

```bash
git clone https://github.com/llm-workflow-engine/lwe-plugin-pastebin.git
```

Install the development package:

```bash
cd llm-workflow-engine
pip install -e .
```

## Configuration

Add the following to `config.yaml` in your profile:

```yaml
plugins:
  enabled:
    - pastebin
    # Any other plugins you want enabled...
  # These are the default values.
  pastebin:
    paste_defaults:
      # When the paste will expire, valid values are:
      # N = Never
      # 10M = 10 Minutes
      # 1H = 1 Hour
      # 1D = 1 Day
      # 1W = 1 Week
      # 2W = 2 Weeks
      # 1M = 1 Month
      # 6M = 6 Months
      # 1Y = 1 Year
      expire: N
      format: text
      # Valid values: public, unlisted, private
      visibility: public
```

## Usage

Use the `/pastebin` command to store the contents of the current conversation to [https://pastebin.com](https://pastebin.com).

Format is `/pastebin [public|unlisted|private] [expire] [custom title]`

From a running LWE shell:

```
# Use the defaults.
/pastebin
# An unlisted paste.
/pastebin unlisted
# Custom everything
/pastebin public 10M My custom title
```
