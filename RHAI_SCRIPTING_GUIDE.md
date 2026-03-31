# Krakiun Agent — Rhai Scripting & Automation Guide

> Complete reference for writing automations, AI-callable tools, and distributable extensions for Krakiun Agent. This document is optimized for both human developers and AI assistants.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Language Basics](#language-basics)
- [Built-in Functions Reference](#built-in-functions-reference)
- [Return Formats](#return-formats)
- [MCP Tools Bridge](#mcp-tools-bridge)
- [Defining AI-Callable Tools](#defining-ai-callable-tools)
- [Concurrency](#concurrency)
- [Persistent Storage](#persistent-storage)
- [HTTP Requests](#http-requests)
- [Todo / Kanban Board](#todo--kanban-board)
- [Knowledge Base & RAG](#knowledge-base--rag)
- [Python Sandbox](#python-sandbox)
- [Provider Security](#provider-security)
- [Error Handling](#error-handling)
- [Limits & Quotas](#limits--quotas)
- [Scheduling](#scheduling)
- [Creating External MCP Servers](#creating-external-mcp-servers)
- [Exporting & Distributing (.krakiun)](#exporting--distributing-krakiun)
- [Known Limitations](#known-limitations)
- [Quick Reference Card](#quick-reference-card)
- [Rhai Gotchas](#rhai-gotchas)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Design Patterns](#design-patterns)
- [Limitations & Workarounds](#limitations--workarounds)
- [Debugging](#debugging)
- [Common Recipes](#common-recipes)
- [Best Practices](#best-practices)
- [Complete Examples](#complete-examples)

---

## Overview

Krakiun Agent automations are scripts written in [Rhai](https://rhai.rs), a lightweight embeddable scripting language for Rust. Scripts can:

- Query any configured AI model (OpenAI, Anthropic, DeepSeek, Mistral, Google, xAI, OpenRouter, Ollama)
- Search the web, read web pages, make HTTP requests
- Read/write files, execute shell commands
- Send emails and Telegram notifications
- Manage Kanban boards and knowledge bases
- Define custom AI-callable tools
- Be compiled to protected binaries (.krakiun) for distribution

**Where to write**: Settings > Automations (Rhai Editor)
**How to run**: Click the bolt icon next to the chat input, select your automation, type a query, press Send.

### Injected Variables

Every script receives these variables automatically:

| Variable | Type | Description |
|----------|------|-------------|
| `query` | String | The text the user typed before running the automation |
| `WORKING_DIR` | String | The working folder path (auto-generated at `~/.krakiun/chat/{conversation_id}` or set in automation settings) |

No other variables are injected. There is no access to user info, app version, or OS environment variables. Use `secret("KEY")` for custom configuration values.

---

## Quick Start

```rhai
// Minimal automation: search the web and summarize results
let results = web_search(query, 5);
let summary = prompt("Summarize these search results:\n" + results);
print(summary);
save_file("summary.md", summary);
```

---

## Language Basics

Rhai is a dynamically-typed scripting language. Full reference: https://rhai.rs/book/

### Variables & Types

```rhai
let x = 42;                    // Integer (i64)
let pi = 3.14;                 // Float (f64)
let name = "hello";            // String
let flag = true;               // Boolean
let items = [1, 2, 3];         // Array
let config = #{ key: "val" };  // Map (object)
```

### Strings

```rhai
let s = "Hello " + "World";   // Concatenation with +
s.len();                       // Length (bytes, not chars)
s.contains("World");           // Boolean check
s.split(" ");                  // Split to array
s.trim();                      // Trim whitespace
s.to_upper();                  // "HELLO WORLD"
s.to_lower();                  // "hello world"
s.starts_with("Hello");        // true
s.sub_string(0, 5);            // "Hello" (start, length)
s.replace("World", "Rhai");    // "Hello Rhai"
```

### Arrays

```rhai
let arr = [1, 2, 3];
arr.push(4);                   // [1, 2, 3, 4]
arr.len();                     // 4
arr[0];                        // 1
arr.pop();                     // Removes and returns last element

for item in arr {
    print(item);
}

// reduce — combine all elements into a single value
let sum = [1, 2, 3].reduce(|total, x| total + x, 0);   // 6
let joined = ["a", "b", "c"].reduce(|a, b| a + ", " + b, "");  // ", a, b, c"

// filter and map (via for loop — Rhai has no built-in filter/map)
let evens = [];
for x in [1, 2, 3, 4, 5] {
    if x % 2 == 0 { evens.push(x); }
}
// evens = [2, 4]
```

### Maps

```rhai
let m = #{ name: "Alice", age: 30 };
m.name;                        // "Alice"
m["age"];                      // 30
m.email = "alice@example.com"; // Add new key
m.contains("name");            // true
m.keys();                      // ["name", "age", "email"]
```

### Control Flow

```rhai
// If/else
if x > 10 {
    print("big");
} else if x > 5 {
    print("medium");
} else {
    print("small");
}

// For loop
for item in [1, 2, 3] { print(item); }

// While loop
let i = 0;
while i < 10 { i += 1; }

// Loop with break
loop {
    if condition { break; }
}
```

### Functions

```rhai
fn greet(name) {
    "Hello, " + name + "!"   // Last expression is the return value
}

fn add(a, b) { a + b }

let msg = greet("World");  // "Hello, World!"
```

### Multi-line Strings (Backticks)

Rhai supports multi-line strings with backticks. This is essential for building JSON payloads:

```rhai
let json = `{
    "channel": "#general",
    "text": "Hello from Krakiun!"
}`;

// Combine with variables using concatenation
let payload = `{"name": "` + user_name + `", "age": ` + age.to_string() + `}`;
```

Backtick strings preserve newlines, tabs, and do not require escaping quotes.

### Type Conversions

```rhai
let n = 42;
n.to_string();    // "42"
"123".to_int();   // 123 (i64)
"3.14".to_float(); // 3.14 (f64)
```

### Working with JSON

Use `parse_json()` and `to_json()` for JSON handling:

```rhai
// Parse JSON string → Rhai Map
let response = http_get("https://api.example.com/users");
let data = parse_json(response);

// Access fields like a normal Map
let name = data["users"][0]["name"];
let email = data["users"][0]["email"];
print("User: " + name + " <" + email + ">");

// Iterate arrays
for user in data["users"] {
    print(user["name"] + ": " + user["role"]);
}

// Build a Map and convert to JSON
let payload = #{
    channel: "#general",
    text: "Hello from Krakiun!",
    blocks: [#{ type: "section", text: #{ type: "mrkdwn", text: "Hello *world*" } }]
};
let json_string = to_json(payload);
http_post("https://slack.com/api/chat.postMessage", headers, json_string);
```

---

## Built-in Functions Reference

### AI Prompting

| Function | Returns | Description |
|----------|---------|-------------|
| `prompt(text)` | String | Send a prompt using the user's selected model. **Preferred for distributable scripts.** |
| `prompt(model, text)` | String | Send a prompt to a specific model. Use when a particular model is required. |
| `parallel_prompt(prompts)` | Array\<String\> | Run multiple prompts concurrently. Each element: a string (default model) or `[model, text]`. Failed prompts return `"ERROR: message"` without stopping the batch. |

**Supported model IDs:**

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| Anthropic | `claude-opus-4-5`, `claude-sonnet-4-5`, `claude-haiku-4-5`, `claude-3-5-sonnet-20241022` |
| DeepSeek | `deepseek-chat`, `deepseek-coder` |
| Mistral | `mistral-large-latest`, `mistral-small-latest`, `codestral-latest`, `open-mistral-nemo` |
| Google | `gemini-2.0-flash`, `gemini-1.5-pro`, `gemini-1.5-flash` |
| xAI | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-2-vision-1212` |
| OpenRouter | `openrouter/...` (any model on OpenRouter) |
| Ollama | `ollama/llama3`, `ollama/mistral`, etc. (local models) |

API keys are configured in Settings > API and are automatically used by the engine. You do not handle API keys in scripts.

```rhai
// Recommended: user picks model
let answer = prompt("Explain quantum computing in simple terms");

// Explicit model: when you need a specific capability
let code = prompt("deepseek-coder", "Write a Python function to sort a list");

// Parallel: 3x faster than sequential
let results = parallel_prompt([
    "Summarize topic A",
    "Summarize topic B",
    ["deepseek-coder", "Write unit tests for function X"],
]);
// results[0], results[1], results[2]
```

### Web & Search

| Function | Returns | Description |
|----------|---------|-------------|
| `web_search(query, max_results)` | String | Search the web via Tavily API. Returns formatted results (see [Return Formats](#return-formats)). |
| `read_url(url)` | String | Extract clean text/markdown content from a web page via Jina API. |
| `parallel_web_search(queries)` | Array\<String\> | Run multiple searches concurrently. Pass array of query strings. |

### File Operations

| Function | Returns | Description |
|----------|---------|-------------|
| `save_file(filename, content)` | void | Save a file to the working folder. Creates parent directories. Relative paths resolved from `WORKING_DIR`. |
| `read_file(path)` | String | Read a file. Relative paths resolved from `WORKING_DIR`. Absolute paths validated against allowed folders. |

**Path security**: `..` traversal and symlink escapes are blocked. Absolute paths must be within folders authorized in Settings > MCP Tools.

### User Interaction

| Function | Returns | Description |
|----------|---------|-------------|
| `ask_user(question)` | String | Pause and ask the user a question. Default timeout: 600s (10 min). |
| `ask_user(question, timeout)` | String | Ask with custom timeout in seconds. `0` = 24h max. |
| `print(message)` | void | Display a message in the automation timeline (visible in chat). |
| `notify(title, message)` | void | Send a push notification via Telegram (requires bot configured in Settings > API). |

### System & Time

| Function | Returns | Description |
|----------|---------|-------------|
| `timestamp()` | String | Current date/time as `"YYYY-MM-DD HH:MM:SS"` (local timezone). |
| `working_dir()` | String | Returns the current working folder path. Same as `WORKING_DIR` variable. |
| `wait(seconds)` | void | Pause execution. Cancellable by user (checks every 200ms). |
| `secret(key)` | String | Read a custom secret from Settings > Automations > Secrets. Returns `""` if key does not exist. |

### JSON

| Function | Returns | Description |
|----------|---------|-------------|
| `parse_json(text)` | Map or Array | Parse a JSON string into a Rhai Map or Array. Throws on invalid JSON. |
| `to_json(value)` | String | Convert any Rhai value (Map, Array, String, number, bool) to pretty-printed JSON. |

```rhai
let data = parse_json(`{"name": "Alice", "scores": [95, 87, 92]}`);
print(data["name"]);           // "Alice"
print(data["scores"][0]);      // 95

let json = to_json(#{ status: "ok", count: 42 });
// {"count": 42, "status": "ok"}
```

### Regex

| Function | Returns | Description |
|----------|---------|-------------|
| `regex_match(text, pattern)` | Array | Find all matches. Returns capture groups if defined, otherwise full matches. |
| `regex_replace(text, pattern, replacement)` | String | Replace all matches. Supports `$1`, `$2` capture group references. |

```rhai
// Extract all emails
let emails = regex_match("Contact alice@x.com or bob@y.com", r"[\w.]+@[\w.]+");
// ["alice@x.com", "bob@y.com"]

// Extract with capture groups
let pairs = regex_match("name=Alice age=30", r"(\w+)=(\w+)");
// ["name", "Alice", "age", "30"]

// Replace
let clean = regex_replace("Hello   World", r"\s+", " ");
// "Hello World"
```

### Encoding & Hashing

| Function | Returns | Description |
|----------|---------|-------------|
| `base64_encode(text)` | String | Encode text to Base64 |
| `base64_decode(text)` | String | Decode Base64 to text. Throws on invalid input. |
| `hash_sha256(text)` | String | SHA-256 hash as lowercase hex (64 chars) |
| `hash_md5(text)` | String | MD5 hash as lowercase hex (32 chars). Use for checksums, not security. |

```rhai
let encoded = base64_encode("Hello World");  // "SGVsbG8gV29ybGQ="
let decoded = base64_decode(encoded);         // "Hello World"

let hash = hash_sha256("password123");  // "ef92b778..."
let checksum = hash_md5(file_content);  // "d41d8cd9..."
```

### Logging

| Function | Returns | Description |
|----------|---------|-------------|
| `log(level, message)` | void | Structured log. Level: `"debug"`, `"info"`, `"warn"`, `"error"`. Visible in timeline and DevTools. |

```rhai
log("info", "Starting process");
log("warn", "Rate limit approaching");
log("error", "API call failed: " + err);
log("debug", "Response length: " + data.len().to_string());
```

### HTTP JSON (most common pattern)

| Function | Returns | Description |
|----------|---------|-------------|
| `http_get_json(url)` | Map/Array | GET + auto-parse JSON response. Throws on HTTP or JSON error. |
| `http_post_json(url, headers, data)` | Map/Array | POST Map as JSON + auto-parse response. Headers as Map. |

```rhai
// Before: 3 lines
let r = http_get_full("https://api.github.com/repos/rust-lang/rust");
let repo = parse_json(r.body);

// After: 1 line
let repo = http_get_json("https://api.github.com/repos/rust-lang/rust");
print("Stars: " + repo["stargazers_count"].to_string());

// POST with JSON body
let headers = #{ "Authorization": "Bearer " + secret("TOKEN") };
let result = http_post_json("https://api.example.com/items", headers, #{
    title: "New Item",
    priority: 1
});
print("Created ID: " + result["id"].to_string());
```

### Text & URL Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `extract_urls(text)` | Array | Extract all `http://` and `https://` URLs from text |
| `lines(text)` | Array | Split by newlines, skip empty lines, trim whitespace |
| `slugify(text)` | String | Convert to URL/filename-safe: `"Hello World!"` → `"hello-world"` |
| `truncate(text, max)` | String | Truncate to `max` chars + `"..."` if needed |
| `url_encode(text)` | String | URL-encode: spaces → `%20`, `&` → `%26`, etc. |
| `prompt_template(template, vars)` | String | Interpolate `${key}` placeholders from a map |
| `extract_json(text)` | Map/Array | Find and parse first `{...}` or `[...]` in text. Great for AI responses with JSON. |
| `split_chunks(text, max)` | Array | Split text into ~max char chunks at paragraph/word boundaries. Min 100. |
| `strip_html(text)` | String | Remove HTML tags and decode entities (`&amp;` → `&`, `&lt;` → `<`, etc.) |
| `unique(array)` | Array | Remove duplicates (preserves order, compares by string value) |
| `count_tokens(text)` | i64 | Approximate token count (~4 chars/token). Check context window fit. |

```rhai
// Extract URLs from search results (replaces 6-line loop)
let urls = extract_urls(web_search("topic", 5));
for url in urls {
    let content = read_url_safe(url);
    if content.len() > 0 { print("Read: " + truncate(content, 200)); }
}

// Split text into clean lines (replaces split+filter+trim loop)
let items = lines(search_queries_text);
// ["query 1", "query 2", "query 3"] — no empty lines

// Template-based prompts (replaces long concatenation chains)
let report = prompt(prompt_template(
    "Write a ${length} report about ${topic}. Focus on: ${focus}. Language: ${lang}.",
    #{ topic: query, focus: "recent developments", length: "500-word", lang: "English" }
));

// URL building
let url = "https://api.example.com/search?q=" + url_encode("rust async") + "&limit=10";

// Filename from title
save_file(slugify("My Research Report 2025") + ".md", content);
// saves: my-research-report-2025.md
```

```rhai
// Extract JSON from AI response that wraps it in explanation text
let raw = prompt("Return the user data as JSON: " + query);
// raw = "Here is the JSON:\n{\"name\": \"Alice\", \"age\": 30}\nLet me know if..."
let data = extract_json(raw);  // #{name: "Alice", age: 30}

// Split large document into chunks for parallel processing
let doc = read_file("large_document.md");
let chunks = split_chunks(doc, 4000);
print("Split into " + chunks.len().to_string() + " chunks");
let summaries = parallel_prompt(chunks);  // Each chunk summarized by AI

// Check token count before sending to AI
if count_tokens(document) > 100000 {
    print("Document too large, chunking...");
}

// Clean HTML from web content
let page = read_url("https://example.com");
let clean = strip_html(page);

// Deduplicate URLs from multiple searches
let urls1 = extract_urls(web_search("topic A", 5));
let urls2 = extract_urls(web_search("topic B", 5));
let all_urls = unique(urls1 + urls2);  // No duplicates
```

### File Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `file_exists(path)` | bool | Check if file exists. Relative or absolute path. No error thrown. |
| `append_file(path, content)` | void | Append to file (creates if missing). Path validated against working folder. |

```rhai
// Check before reading (no more try/catch for existence check)
if file_exists("previous_results.md") {
    let old = read_file("previous_results.md");
    print("Found previous results: " + truncate(old, 100));
}

// Append to log file (no need to read + concatenate + write)
append_file("run_log.txt", timestamp() + " — Run completed\n");
append_file("results.csv", query + "," + result.replace(",", ";") + "\n");
```

### Secrets & Storage Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `require_secrets(keys)` | Map | Validate all secrets exist; throws `"Missing required secrets: KEY1, KEY2. Set them in Settings > Automations > Secrets."` if any are missing or empty. Returns `#{KEY: "value"}`. |
| `store_increment(key)` | i64 | Increment persistent counter by 1, return new value. Creates key if missing. |
| `store_get_json(key)` | Map/Array | Read structured data from store. Returns parsed Map/Array, or `()` if missing. |
| `store_set_json(key, value)` | void | Store a Map or Array as JSON. |

```rhai
// Validate secrets in one line (replaces 4-6 line check)
let creds = require_secrets(["API_TOKEN", "WEBHOOK_URL"]);
let token = creds["API_TOKEN"];  // guaranteed non-empty

// Track run count (replaces 3-line get/parse/set pattern)
let run_number = store_increment("daily_report_runs");
print("Run #" + run_number.to_string());
```

```rhai
// Store structured data (not just strings)
store_set_json("last_results", #{ query: query, count: 5, urls: urls });
let prev = store_get_json("last_results");
if prev.type_of() != "()" {
    print("Previous query: " + prev["query"]);
}
```

### Date Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `date_add(timestamp, days)` | String | Add/subtract days. Negative days to go back. Returns `"YYYY-MM-DD HH:MM:SS"`. |
| `date_diff(ts1, ts2)` | i64 | Difference in seconds (ts2 - ts1). Positive if ts2 is later. |
| `format_date(timestamp, format)` | String | Custom format: `%Y`=year, `%m`=month, `%d`=day, `%H`=hour, `%M`=min, `%A`=weekday. |
| `today()` | String | Current date at midnight: `"YYYY-MM-DD 00:00:00"`. |
| `now()` | String | Current timestamp. Alias for `timestamp()`. |
| `day_name(timestamp)` | String | `"Monday"`, `"Tuesday"`, etc. Accepts `"YYYY-MM-DD"` or full timestamp. |
| `month_name(timestamp)` | String | `"January"`, `"February"`, etc. |
| `is_business_day(date)` | bool | `true` if Monday-Friday. |
| `next_business_day(date)` | String | Next Monday-Friday after the given date. |

```rhai
let now = timestamp();  // "2025-03-28 14:30:00"

// When was 7 days ago?
let week_ago = date_add(now, -7);  // "2025-03-21 14:30:00"

// How many seconds between two timestamps?
let diff = date_diff("2025-03-01 00:00:00", now);
let days = diff / 86400;
print("Days since March 1: " + days.to_string());

// Format for display
let pretty = format_date(now, "%A, %B %d %Y");  // "Friday, March 28 2025"
let iso = format_date(now, "%Y-%m-%dT%H:%M:%S");  // "2025-03-28T14:30:00"
```

### Safe Network

| Function | Returns | Description |
|----------|---------|-------------|
| `read_url_safe(url)` | String | Read URL content; returns `""` on error instead of throwing. Cancellation is still thrown. |
| `web_search_json(query, max)` | Array | Web search returning `[#{title, url, snippet}, ...]` instead of raw text. |

```rhai
// Read URL without try/catch boilerplate (replaces 4-5 line pattern)
let content = read_url_safe("https://example.com/page");
if content.len() > 0 {
    print("Got content: " + truncate(content, 100));
}

// Structured search results (replaces manual URL extraction)
let results = web_search_json("rust programming", 5);
for r in results {
    print(r["title"] + " — " + r["url"]);
    let page = read_url_safe(r["url"]);
    wait(1);
}
```

### Advanced Time & Files

| Function | Returns | Description |
|----------|---------|-------------|
| `sleep_until(timestamp)` | void | Wait until `"YYYY-MM-DD HH:MM:SS"` (local timezone). Cancellable. Returns immediately if timestamp is in the past. Throws on invalid format. |
| `list_files(path, pattern)` | Array | Glob files matching pattern. Returns array of relative file path strings. Max 200 results. Throws if path doesn't exist or is not in allowed folders. |

```rhai
// Wait until 2:30 PM today
sleep_until("2025-03-28 14:30:00");

// List all Rust source files
let files = list_files("/home/user/project", "**/*.rs");
for f in files {
    print("Found: " + f);
}
```

### IDs & Random Numbers

| Function | Returns | Description |
|----------|---------|-------------|
| `uuid()` | String | Random UUID v4: `"550e8400-e29b-41d4-a716-446655440000"` |
| `short_id(length)` | String | Random alphanumeric string (1-64 chars) |
| `random_int(min, max)` | i64 | Random integer in [min, max] inclusive |
| `random_float()` | f64 | Random float between 0.0 and 1.0 |

```rhai
let id = uuid();                    // "550e8400-e29b-..."
let tracking = short_id(8);         // "k3m9x2pq"
let dice = random_int(1, 6);       // 1-6
let chance = random_float();        // 0.0-1.0
```

### HMAC & Crypto

| Function | Returns | Description |
|----------|---------|-------------|
| `hmac_sha256(key, message)` | String | HMAC-SHA256 hex digest |
| `hmac_verify(key, data, signature)` | bool | Verify HMAC-SHA256. Strips `"sha256="` prefix automatically. |
| `encrypt(data, password)` | String | AES-256-GCM encrypt → base64 |
| `decrypt(encrypted, password)` | String | Decrypt → original text. Throws on wrong password. |

```rhai
// Verify GitHub webhook signature
let sig = headers["x-hub-signature-256"];
assert(hmac_verify(secret("GITHUB_SECRET"), body, sig), "Invalid webhook signature");

// Encrypt sensitive data before storing
let encrypted = encrypt("sensitive data", secret("ENCRYPTION_KEY"));
store_set("encrypted_data", encrypted);
let original = decrypt(store_get("encrypted_data"), secret("ENCRYPTION_KEY"));
```

### String Case Conversions

| Function | Returns | Description |
|----------|---------|-------------|
| `title_case(text)` | String | `"hello world"` → `"Hello World"` |
| `snake_case(text)` | String | `"HelloWorld"` → `"hello_world"` |
| `camel_case(text)` | String | `"hello_world"` → `"helloWorld"` |
| `pascal_case(text)` | String | `"hello_world"` → `"HelloWorld"` |
| `kebab_case(text)` | String | `"HelloWorld"` → `"hello-world"` |

```rhai
let api_field = snake_case("UserName");   // "user_name"
let js_var = camel_case("user_name");     // "userName"
let css_class = kebab_case("MyComponent"); // "my-component"
let heading = title_case("hello world");   // "Hello World"
```

### String Formatting

| Function | Returns | Description |
|----------|---------|-------------|
| `pad_left(text, width, char)` | String | Left-pad: `pad_left("42", 5, "0")` → `"00042"` |
| `pad_right(text, width, char)` | String | Right-pad: `pad_right("hi", 10, ".")` → `"hi........"` |
| `repeat_str(text, count)` | String | `repeat_str("ab", 3)` → `"ababab"` |
| `word_count(text)` | i64 | Count words (splits on whitespace) |
| `format_number(num, decimals)` | String | `format_number(1234567, 2)` → `"1,234,567.00"` |
| `format_bytes(bytes)` | String | `format_bytes(1234567)` → `"1.2 MB"` |
| `format_duration(seconds)` | String | `format_duration(3661)` → `"1h 1m 1s"` |
| `to_hex(num)` | String | `to_hex(255)` → `"ff"` |
| `from_hex(text)` | i64 | `from_hex("ff")` → `255` |
| `url_decode(text)` | String | `url_decode("%20")` → `" "` |
| `word_wrap(text, width)` | String | Wrap text at word boundaries |
| `normalize_text(text)` | String | Lowercase + remove diacritics: `"Café"` → `"cafe"` |

### Path Operations

| Function | Returns | Description |
|----------|---------|-------------|
| `path_join(parts)` | String | Cross-platform path join: `path_join(["home", "user", "file.txt"])` |
| `path_basename(path)` | String | `"/home/user/file.txt"` → `"file.txt"` |
| `path_dirname(path)` | String | `"/home/user/file.txt"` → `"/home/user"` |
| `path_extension(path)` | String | `"file.txt"` → `"txt"` |
| `file_size(path)` | i64 | File size in bytes |
| `file_modified_at(path)` | String | Last modified as `"YYYY-MM-DD HH:MM:SS"` |
| `env_var(name)` | String | Read OS environment variable. `""` if not set. |
| `temp_dir()` | String | System temporary directory path |
| `dir_exists(path)` | bool | Check if directory exists |
| `copy_file(src, dest)` | String | Copy file. Returns confirmation. |
| `create_dir(path)` | void | Create directory (and parents) |
| `delete_dir(path)` | void | Delete directory recursively |

```rhai
let ext = path_extension("/project/data.csv");    // "csv"
let name = path_basename("/project/data.csv");     // "data.csv"
let dir = path_dirname("/project/data.csv");       // "/project"
let full = path_join(["/home", "user", "docs"]);   // "/home/user/docs"

let size = file_size("report.pdf");
print("File: " + format_bytes(size));  // "File: 2.3 MB"

let home = env_var("HOME");           // "/Users/alice"
let tmp = temp_dir();                  // "/tmp"
```

### File Editing (Claude Code style)

| Function | Returns | Description |
|----------|---------|-------------|
| `edit_file(path, old_text, new_text)` | String | Find-and-replace. `old_text` must be unique and exact match. |
| `insert_lines(path, line, content)` | String | Insert before line number (1-indexed). |

```rhai
// Edit: replace specific text (must be unique in file)
call_mcp("edit_file", #{
    path: "/project/config.json",
    old_text: `"debug": false`,
    new_text: `"debug": true`
});

// Insert: add lines before line 5
call_mcp("insert_lines", #{
    path: "/project/main.rs",
    line: 5,
    content: "use std::collections::HashMap;\nuse std::io;"
});

// Read specific lines (1-indexed)
let header = call_mcp("read_file", #{ path: "/project/main.rs", start_line: 1, end_line: 20 });
```

### Array Operations (Extended)

| Function | Returns | Description |
|----------|---------|-------------|
| `zip(arr1, arr2)` | Array | Combine into `[[a,b], ...]` pairs |
| `enumerate_arr(arr)` | Array | Add indices: `[[0,val], [1,val], ...]` |
| `range(start, end)` | Array | Integer sequence `[start, ..., end-1]` |
| `range_step(start, end, step)` | Array | With custom step |
| `reverse(arr)` | Array | Reversed copy |
| `intersect(arr1, arr2)` | Array | Common elements |
| `difference(arr1, arr2)` | Array | In arr1 but not arr2 |
| `keys(map)` | Array | Map keys as array |
| `values(map)` | Array | Map values as array |
| `entries(map)` | Array | `[[key, val], ...]` |
| `unique_by(arr, field)` | Array | Deduplicate maps by field |
| `count_by(arr, field)` | Map | Frequency count: `#{val: count}` |
| `min_by(arr, field)` | Dynamic | Element with minimum field value |
| `max_by(arr, field)` | Dynamic | Element with maximum field value |
| `sliding_window(arr, size)` | Array | Overlapping windows |

```rhai
// Zip two arrays
let names = ["Alice", "Bob"];
let scores = [95, 87];
let pairs = zip(names, scores);   // [["Alice", 95], ["Bob", 87]]

// Generate number sequences
let nums = range(1, 11);          // [1, 2, ..., 10]
let evens = range_step(0, 20, 2); // [0, 2, 4, ..., 18]

// Set operations
let a = [1, 2, 3, 4];
let b = [3, 4, 5, 6];
intersect(a, b);    // [3, 4]
difference(a, b);   // [1, 2]

// Data analysis
let orders = parse_csv(read_file("orders.csv"));
let by_status = count_by(orders, "status");  // #{pending: 5, shipped: 12}
let cheapest = min_by(orders, "price");
let most_expensive = max_by(orders, "price");
```

### Config Formats

| Function | Returns | Description |
|----------|---------|-------------|
| `yaml_parse(text)` | Map/Array | Parse YAML string |
| `yaml_stringify(value)` | String | Value → YAML string |
| `toml_parse(text)` | Map | Parse TOML string |
| `toml_stringify(value)` | String | Value → TOML string |

```rhai
// Parse YAML config
let config = yaml_parse(read_file("config.yml"));
print("Database: " + config["database"]["host"]);

// Parse Cargo.toml
let cargo = toml_parse(read_file("Cargo.toml"));
print("Package: " + cargo["package"]["name"]);

// Generate YAML
let data = #{ name: "app", version: "1.0", debug: false };
save_file("output.yml", yaml_stringify(data));
```

### Text Extractors

| Function | Returns | Description |
|----------|---------|-------------|
| `extract_emails(text)` | Array | All email addresses (deduplicated) |
| `extract_numbers(text)` | Array\<f64\> | All numbers including `1,234.56` |
| `extract_phone_numbers(text)` | Array | Phone numbers (7+ digits) |

```rhai
let text = "Contact alice@x.com or bob@y.com. Call +1 (555) 123-4567. Price: $1,299.99";
let emails = extract_emails(text);   // ["alice@x.com", "bob@y.com"]
let phones = extract_phone_numbers(text);  // ["+1 (555) 123-4567"]
let nums = extract_numbers(text);    // [1.0, 555.0, 123.0, 4567.0, 1299.99]
```

### HTML Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `html_links(html)` | Array | All `href` URLs (deduplicated) |
| `html_text(html)` | String | Strip tags + decode entities (alias for `strip_html`) |
| `html_select(html, tag)` | Array | Inner text of all matching **tag names** (e.g., `"h2"`, `"p"`, `"a"`). Not a CSS selector — only tag names work. |

```rhai
let page = http_get("https://example.com");
let links = html_links(page);          // ["https://...", ...]
let headings = html_select(page, "h2"); // ["Section 1", "Section 2", ...]
let clean = html_text(page);            // Plain text, no HTML
```

### Network Utilities

| Function | Returns | Description |
|----------|---------|-------------|
| `dns_lookup(hostname)` | String | Resolve hostname → IP address |
| `port_check(host, port)` | bool | Check if TCP port is open (3s timeout) |
| `http_health_check(url)` | Map | `#{ok: bool, status: int, latency_ms: int}` |
| `graphql_query(url, query, variables, headers)` | Map | Execute GraphQL query. Returns full response map including `data` and `errors` fields (GraphQL returns HTTP 200 even on errors). Check `result["errors"]` for query errors. |
| `rss_parse(url_or_xml)` | Array | Parse RSS/Atom → `[#{title, url, content, date, author}]`. Missing fields return `""` (empty string, never `()`). |

```rhai
// Check if service is running
if port_check("localhost", 5432) { print("PostgreSQL is up"); }

// Monitor API endpoint
let health = http_health_check("https://api.example.com/health");
if !health["ok"] { notify("API Down", "Status: " + health["status"].to_string()); }

// GraphQL query
let headers = #{ "Authorization": "Bearer " + secret("GITHUB_TOKEN") };
let result = graphql_query("https://api.github.com/graphql",
    `{ viewer { login repositories(first: 5) { nodes { name } } } }`,
    #{}, headers
);
print("GitHub user: " + result["data"]["viewer"]["login"]);

// Parse RSS feed
let articles = rss_parse("https://blog.rust-lang.org/feed.xml");
for a in articles {
    print(a["title"] + " — " + a["date"]);
}
```

### Auth Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `basic_auth_header(user, pass)` | String | `"Basic base64(user:pass)"` |
| `jwt_decode(token)` | Map | Decode JWT claims (no verification) |
| `oauth2_token(client_id, secret, url, scope)` | Map | Get OAuth2 token. Returns `#{access_token, token_type, expires_in, scope}`. Fields depend on provider. |
| `json_diff(obj1, obj2)` | Map | `#{added: [...], removed: [...], changed: [...]}` |

```rhai
// WordPress auth
let auth = basic_auth_header("admin", secret("WP_PASS"));

// Decode JWT (inspect claims without verification)
let claims = jwt_decode(token);
print("User: " + claims["sub"] + ", Expires: " + claims["exp"].to_string());

// OAuth2 (Google, Microsoft, Salesforce, etc.)
let token_resp = oauth2_token(
    secret("CLIENT_ID"), secret("CLIENT_SECRET"),
    "https://oauth2.googleapis.com/token", "https://www.googleapis.com/auth/drive.readonly"
);
let access_token = token_resp["access_token"];

// Detect API response changes
let old_data = store_get_json("api_snapshot");
let new_data = http_get_json("https://api.example.com/config");
if old_data.type_of() != "()" {
    let diff = json_diff(old_data, new_data);
    if diff["changed"].len() > 0 { notify("Config Changed", to_json(diff["changed"])); }
}
store_set_json("api_snapshot", new_data);
```

### Templates

| Function | Returns | Description |
|----------|---------|-------------|
| `prompt_template(template, vars)` | String | Interpolate `${key}` placeholders |
| `render_template(template, vars)` | String | Interpolate `{{key}}` placeholders (Mustache/Jinja2 style) |

Both do the same thing but with different placeholder syntax. Use whichever matches your preference:

```rhai
// ${key} style (JavaScript-like)
let msg = prompt_template("Hello ${name}, you have ${count} items.", #{
    name: "Alice", count: 5
});

// {{key}} style (Mustache/Jinja2-like)
let html = render_template("<h1>{{title}}</h1><p>{{body}}</p>", #{
    title: "Welcome", body: "Hello world"
});
```

### AI Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `prompt_json(prompt, schema)` | Map/Array | Prompt AI + force JSON response. Schema is a text description of expected fields. |
| `chat(messages)` | String | Multi-turn conversation. Pass `[#{role: "user", content: "..."}, ...]`. |

```rhai
// Structured extraction — guaranteed JSON response
let data = prompt_json(
    "Extract the person's info from: " + text,
    '{"name": "string", "email": "string", "age": "number"}'
);
print(data["name"] + " <" + data["email"] + ">");

// Multi-turn conversation
let messages = [
    #{ role: "system", content: "You are a helpful translator." },
    #{ role: "user", content: "Translate 'hello' to French" },
    #{ role: "assistant", content: "Bonjour" },
    #{ role: "user", content: "Now to German" },
];
let response = chat(messages);  // "Hallo"
```

### Data Format Helpers

| Function | Returns | Description |
|----------|---------|-------------|
| `parse_csv(text)` | Array\<Map\> | CSV → array of maps. Header row → keys. Handles quoted fields. |
| `to_csv(data)` | String | Array of maps → CSV string. |
| `markdown_to_html(text)` | String | Markdown → HTML. Headings, bold, italic, code, links, lists. |

```rhai
// Parse CSV data
let csv = read_file("contacts.csv");
let rows = parse_csv(csv);  // [#{name: "Alice", email: "alice@x.com"}, ...]
for row in rows {
    print(row["name"] + ": " + row["email"]);
}

// Generate CSV
let data = [#{ name: "Bob", score: "95" }, #{ name: "Carol", score: "87" }];
save_file("results.csv", to_csv(data));

// Convert AI markdown to HTML for WordPress/email
let article = prompt("Write a blog post about " + query);
let html = markdown_to_html(article);
```

### Automation Control

| Function | Returns | Description |
|----------|---------|-------------|
| `debounce(key, seconds)` | bool | `true` if OK to proceed, `false` if called too recently. Prevents duplicate runs. |
| `cache_get(key, ttl_secs)` | String | Get cached value if within TTL. `""` if expired/missing. |
| `cache_set(key, value)` | void | Store value with timestamp for TTL checking. |
| `text_diff(old, new)` | String | Line diff: `"- removed\n+ added"`. `"(no changes)"` if identical. |
| `download_file(url, path)` | String | Download binary file (image/PDF/etc). Returns `"Downloaded N bytes to path"`. |

```rhai
// Prevent duplicate email sends
if !debounce("daily_report", 3600) {
    print("Already ran in the last hour, skipping");
    return;  // or just skip the email part
}

// Cache expensive API calls
let cached = cache_get("weather_data", 600);  // 10 min TTL
if cached == "" {
    cached = http_get("https://api.weather.com/...");
    cache_set("weather_data", cached);
}

// Monitor page changes
let current = read_url_safe("https://example.com/pricing");
let previous = store_get("pricing_page");
if previous != "" {
    let changes = text_diff(previous, current);
    if changes != "(no changes)" {
        notify("Price Change Detected", changes);
    }
}
store_set("pricing_page", current);

// Download images
download_file("https://example.com/logo.png", "images/logo.png");
```

---

### Platform & Validation

| Function | Returns | Description |
|----------|---------|-------------|
| `get_platform()` | String | `"macos"`, `"windows"`, or `"linux"` |
| `is_valid_email(text)` | bool | Validate email format |
| `is_valid_url(text)` | bool | Check `http://` or `https://` prefix |
| `is_valid_json(text)` | bool | Check if text is parseable JSON |
| `assert(condition, message)` | void | Throw error if condition is false |

```rhai
// Cross-platform paths
let sep = if get_platform() == "windows" { "\\" } else { "/" };

// Input validation
let email = ask_user("Enter your email:");
assert(is_valid_email(email), "Invalid email: " + email);

// Safe JSON check before parsing
if is_valid_json(response) {
    let data = parse_json(response);
} else {
    let data = extract_json(response);  // Try to extract from text
}
```

### Array Operations

| Function | Returns | Description |
|----------|---------|-------------|
| `sort_by(array, key)` | Array | Sort array of maps by field name (string comparison) |
| `group_by(array, key)` | Map | Group maps by field: `#{val1: [...], val2: [...]}` |
| `flatten(array)` | Array | Flatten one level: `[[1,2],[3]]` → `[1,2,3]` |
| `chunk(array, size)` | Array\<Array\> | Split into batches: `chunk(items, 10)` → 10-item sub-arrays |

```rhai
// Sort search results by title
let results = web_search_json("topic", 10);
let sorted = sort_by(results, "title");

// Group data by category
let rows = parse_csv(read_file("data.csv"));
let by_status = group_by(rows, "status");
print("Pending: " + by_status["pending"].len().to_string());

// Process in batches with rate limiting
let all_urls = extract_urls(web_search("topic", 20));
for batch in chunk(all_urls, 5) {
    for url in batch {
        let content = read_url_safe(url);
        // ... process
    }
    wait(2);  // Rate limit between batches
}

// Flatten nested results (Rhai has no .map() — use for loop)
let searches = parallel_web_search(["A", "B", "C"]);
let all_extracted = [];
for r in searches { all_extracted.push(extract_urls(r)); }
let all_urls = unique(flatten(all_extracted));
```

---

## Return Formats

Exact output formats for functions that return structured data:

### `web_search(query, max_results)` → String

```
Optional Tavily answer paragraph

---
Sources:

**Article Title 1**
https://example.com/article1
First 200 characters of the article snippet...

**Article Title 2**
https://example.com/article2
First 200 characters of the snippet...
```

If Tavily provides a direct answer, it appears first followed by `---\nSources:`. If no answer, sources are listed directly. Each result has three lines: `**title**`, `url`, `snippet` (max 200 chars).

**Parsing URLs from results:**
```rhai
let results = web_search("topic", 5);
for line in results.split("\n") {
    if line.starts_with("http") {
        let url = line.trim();
        // url is a clean URL string
    }
}
```

### `kb_search(query)` → String

```
Found 3 result(s):

**1. "Conversation Title"** (assistant)
> First 200 characters of the matching text snippet...
Score: 87%

**2. "[KB] Document Title"** (knowledge_base)
> First 200 characters of the matching chunk...
Score: 72%
```

Returns `"No results for: \"query\""` if nothing found. KB documents are prefixed with `[KB]`. Score is cosine similarity as percentage (0-100%).

### `kb_index_text(title, content)` → String

```
Indexed 'Document Title' — 5 chunks, doc id: abc-123-def
```

Or if embedding fails: `"Saved 'Title' (doc id: abc-123) but embedding failed: error message"`

### `todo_items()` → String

```
Board: My Project

Column: To Do
  1. [pending] Write unit tests
     Need tests for auth module
     ID: abc-123

  2. [pending] Update docs
     ID: def-456

Column: In Progress
  1. [pending] Fix login bug
     ID: ghi-789
```

### `todo_columns()` → String

```
Board: My Project
Columns:
  1. To Do (3 items)
  2. In Progress (1 item)
  3. Done (5 items) [done column]
```

### `list_directory` (via call_mcp) → String

```
Contents of /home/user/project:

  📁 src
  📁 tests
  📄 Cargo.toml
  📄 README.md
```

### `execute_command` (via call_mcp) → String

On **success** (exit code 0): returns stdout. If stdout is empty, returns `"(no output)"`.
On **failure** (non-zero exit): returns stdout + stderr combined (no exit code number).

```
$ ls /tmp
file1.txt
file2.txt

$ invalid_command
sh: invalid_command: command not found
```

stderr is NOT returned on success. There is no way to get the exit code separately.

### `glob` (via call_mcp) → String

```
Glob results for '*.rs' in /home/user/project:

  src/main.rs
  src/lib.rs
  tests/test_utils.rs
```

Returns `"(no files found)"` if no matches. **Truncated at 200 results** with a warning message.

### `grep` (via call_mcp) → String

```
Grep results for 'TODO' in /home/user/project:

src/main.rs:42: // TODO: refactor this function
src/lib.rs:15: // TODO: add error handling
tests/test.rs:7: // TODO: add more test cases
```

Format: `relative/path:line_number: matched_line_content`. Case-insensitive regex. **Truncated at 100 matches.** Respects `.gitignore`.

### `last_news` / `search_news` / `get_feeds` (via call_mcp) → String

These return human-readable formatted text (not JSON):

**`get_feeds`**: Lists feed names, URLs, and enabled status.
**`last_news`**: Articles formatted as `**Title** (date)\nURL\nDescription snippet`.
**`search_news`**: Same format as `last_news`, filtered by keyword.

### `todo_add` / `todo_done` / `todo_move` / `todo_delete` → String

These return confirmation messages:

```
Added "Write tests" to column "To Do" (id: abc-123)
Marked "Write tests" as done
Moved "Write tests" to "In Progress"
Deleted item abc-123
```

### `store_get(key)` → String

Returns the stored value as a string. Returns **empty string `""`** if the key does not exist (not an error). All stored values are strings.

```rhai
let value = store_get("my_key");
if value == "" {
    print("Key not found or empty");
}
```

### `web_search_json(query, max)` → Array\<Map\>

Returns an array of maps, one per search result:

```
[
  #{ title: "Article Title", url: "https://example.com/article", snippet: "First 200 chars..." },
  #{ title: "Another Result", url: "https://other.com/page", snippet: "Content preview..." }
]
```

Access fields directly: `results[0]["url"]`, `results[0]["title"]`.

### `extract_urls(text)` → Array\<String\>

Returns all URLs found in text:

```
["https://example.com/page1", "https://other.com/article", "http://docs.rs/tokio"]
```

Trailing punctuation (`.`, `,`) is automatically stripped.

### `lines(text)` → Array\<String\>

Splits text by newlines, trims each line, removes empty lines:

```rhai
let items = lines("  hello  \n\n  world  \n  ");
// ["hello", "world"]
```

### `list_files(path, pattern)` → Array\<String\>

Returns array of relative file paths matching the glob pattern:

```
["src/main.rs", "src/lib.rs", "tests/test_utils.rs"]
```

Max 200 results. Only files returned (not directories).

### `regex_match(text, pattern)` → Array\<String\>

Without capture groups — returns all full matches:
```rhai
regex_match("foo@bar.com and baz@qux.com", r"[\w]+@[\w]+\.\w+")
// ["foo@bar.com", "baz@qux.com"]
```

With capture groups — returns all captured groups (flattened):
```rhai
regex_match("name=Alice age=30", r"(\w+)=(\w+)")
// ["name", "Alice", "age", "30"]
```

### `parallel_prompt(prompts)` → Array\<String\>

Returns an array of response strings in the same order as the input array. If an individual prompt fails, its position contains `"ERROR: error message"` instead of throwing — the batch continues.

```rhai
let results = parallel_prompt(["question 1", "question 2"]);
for r in results {
    if r.starts_with("ERROR:") {
        print("Failed: " + r);
    } else {
        print("OK: " + r.sub_string(0, 100));
    }
}
```

---

## MCP Tools Bridge

The `call_mcp(tool, params)` function lets Rhai scripts call **any** backend MCP tool directly.

### Syntax

```rhai
let result = call_mcp("tool_name", #{ param1: "value1", param2: "value2" });
```

### Available MCP Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `read_file` | `path` | Read file contents |
| `write_file` | `path, content` | Write content to a file |
| `delete_file` | `path` | Delete a file |
| `move_file` | `source, destination` | Move or rename a file |
| `list_directory` | `path` | List directory contents (returns 📁/📄 formatted text) |
| `create_directory` | `path` | Create a new directory (and parents) |
| `glob` | `path, pattern` | Match files by glob pattern |
| `grep` | `path, query` | Search file contents by regex |
| `execute_command` | `command, cwd` | Execute a shell command. `cwd` is optional working directory. |
| `web_search` | `query, max_results` | Search the web (Tavily API) |
| `read_url` | `url` | Read web page content (Jina API) |
| `send_webhook` | `url, method, headers, body` | Send HTTP request. Method: GET/POST/PUT/DELETE/PATCH. |
| `send_email_raw` | `to, subject, body` | Send a plain email (SMTP) |
| `send_email_template` | `to, template_name, variables` | Send a templated email with variable substitution |
| `telegram_send` | `message` | Send a Telegram message |
| `telegram_notify` | `title, body` | Send a formatted Telegram notification |
| `get_feeds` | (none) | List configured RSS feeds |
| `last_news` | `limit, feed_id` | Get latest RSS articles. `feed_id` is optional filter. |
| `search_news` | `query, limit, feed_id` | Search RSS articles by keyword |
| `todo_add_item` | `title, description, column` | Add a Kanban task |
| `todo_get_items` | `column` | Get Kanban items (optional column filter) |
| `todo_mark_done` | `id` | Mark task as done |
| `todo_move_item` | `id, column` | Move task between columns |
| `todo_get_next` | `column` | Get next priority task (optional column filter) |
| `rag_search` | `query, limit` | Semantic search across KB + conversations |
| `run_python` | `code, timeout` | Execute Python in sandbox |

### Tool Name Aliases

Tool names are automatically normalized. You can use either the canonical name or common aliases:

| Alias | Resolves To |
|-------|-------------|
| `search`, `web` | `web_search` |
| `read`, `cat` | `read_file` |
| `write`, `save` | `write_file` |
| `delete`, `rm` | `delete_file` |
| `mv`, `rename` | `move_file` |
| `ls`, `dir` | `list_directory` |
| `mkdir` | `create_directory` |
| `shell`, `exec`, `terminal`, `bash` | `execute_command` |
| `python` | `run_python` |

### Notes

- `call_mcp()` bypasses the permission dialog (scripts are user-created and trusted).
- Frontend-only tools (`take_screenshot`, `list_models`, `ask_model`) and custom MCP server tools cannot be called from Rhai.
- Use `try/catch` for error handling — failed tools return strings starting with `"❌"`.

---

## Defining AI-Callable Tools

Turn your automations into tools that the AI discovers and calls automatically during conversations.

### How It Works

1. Add structured comments at the top of your script to define tools
2. Save the script — the editor parses comments and registers tools
3. The AI sees your tools alongside built-in tools (read_file, web_search, etc.)
4. When the AI determines your tool is relevant, it calls the handler function automatically

### Comment Format

```rhai
// TOOL: tool_name
// DESCRIPTION: What the tool does (the AI reads this to decide when to call it)
// PARAM: param_name (type, required) — Description of the parameter
// PARAM: another_param (type, optional) — Description of the parameter
// HANDLER: handler_function_name
```

| Field | Description |
|-------|-------------|
| `TOOL` | Unique name (lowercase, underscores). Becomes `rhai__tool_name` in the AI's tool list. |
| `DESCRIPTION` | What the tool does. Be specific — the AI uses this to decide when to call it. |
| `PARAM` | Parameter. Type: `string`, `number`, or `boolean`. Mark `required` or `optional`. |
| `HANDLER` | Rhai function to call. Must accept a single `args` map parameter. |

### Handler Function Pattern

The handler receives a Rhai map with the parameters the AI provided:

```rhai
fn handle_my_tool(args) {
    // Access required params directly
    let path = args["path"];

    // Check optional params with .contains()
    let limit = if args.contains("limit") { args["limit"] } else { 10 };

    // Return a string result (shown to the AI)
    "Result: " + some_value
}
```

The return value is converted to a string and sent back to the AI as the tool result.

### Example: File Summarizer

```rhai
// TOOL: summarize_file
// DESCRIPTION: Read a file and generate a concise summary of its contents
// PARAM: path (string, required) — Absolute path to the file to summarize
// PARAM: max_words (number, optional) — Maximum words in the summary (default 200)
// HANDLER: handle_summarize_file

fn handle_summarize_file(args) {
    let content = call_mcp("read_file", #{ path: args["path"] });
    let max = if args.contains("max_words") { args["max_words"] } else { 200 };
    prompt("Summarize in " + max.to_string() + " words or less:\n\n" + content)
}
```

### Example: Multiple Tools in One Script

```rhai
// TOOL: count_words
// DESCRIPTION: Count the number of words in a text file
// PARAM: path (string, required) — Path to the file
// HANDLER: handle_count_words

// TOOL: find_todos
// DESCRIPTION: Find all TODO, FIXME, and HACK comments in source code
// PARAM: directory (string, required) — Directory to search recursively
// HANDLER: handle_find_todos

fn handle_count_words(args) {
    let text = call_mcp("read_file", #{ path: args["path"] });
    "File has " + text.split(" ").len().to_string() + " words, " + text.split("\n").len().to_string() + " lines"
}

fn handle_find_todos(args) {
    call_mcp("grep", #{ path: args["directory"], query: "TODO|FIXME|HACK" })
}
```

### Tool Behavior Details

| Aspect | Detail |
|--------|--------|
| **Permissions** | Uses "Ask" permission — user prompted before first use per conversation |
| **Timeout** | 120-second timeout per handler execution |
| **Cancellation** | Users can cancel with the stop button |
| **Secrets** | `secret("key")` works in handlers (loaded from Settings > Automations > Secrets) |
| **Default model** | `prompt("text")` uses the user's currently selected model |
| **Visibility** | Only tools from **enabled** automations appear in the AI's tool list |
| **Persistence** | Tool definitions persist across app restarts (stored in localStorage) |
| **Naming** | Names must be unique across all automations. Duplicates are silently ignored. |
| **Scope** | Rhai tools are local to Krakiun Agent only. For cross-app tools, create an MCP Server. |

---

## Concurrency

Rhai is single-threaded, but `parallel_prompt()` and `parallel_web_search()` run operations concurrently under the hood.

```rhai
// 3 prompts run at the same time — ~3x faster than sequential
let results = parallel_prompt([
    "Summarize topic A",
    "Summarize topic B",
    ["deepseek-coder", "Write tests for function X"],
]);

// Concurrent web searches
let searches = parallel_web_search(["topic A", "topic B", "topic C"]);
```

Use `parallel_prompt()` when you need multiple independent AI responses. Use sequential `prompt()` when each response depends on the previous one.

### Error Handling in Parallel Operations

Both `parallel_prompt()` and `parallel_web_search()` use the same error pattern: failed items return `"ERROR: message"` instead of throwing. The batch continues regardless of individual failures.

```rhai
let results = parallel_web_search(["valid query", "another query"]);
for r in results {
    if r.starts_with("ERROR:") {
        print("Search failed: " + r);
    } else {
        print("Got results: " + r.sub_string(0, 100));
    }
}
```

---

## Persistent Storage

Store values between automation runs using `store_set`, `store_get`, `store_delete`. Data persists in `~/.krakiun/rhai_store.json` across app restarts.

| Function | Returns | Description |
|----------|---------|-------------|
| `store_set(key, value)` | void | Store a string value. Overwrites existing. |
| `store_get(key)` | String | Read value. Returns **empty string `""`** if key doesn't exist. |
| `store_delete(key)` | void | Remove a key. No error if key doesn't exist. |

```rhai
// Track run count
let count = store_get("run_count");
let new_count = if count == "" { 1 } else { count.to_int() + 1 };
store_set("run_count", new_count.to_string());
print("Run #" + new_count.to_string());

// Remember last run time
store_set("last_run", timestamp());
```

**Important**: All values are stored and returned as strings. Use `.to_int()` or `.to_float()` to convert.

---

## HTTP Requests

### Simple (body only)

| Function | Returns | Description |
|----------|---------|-------------|
| `http_get(url)` | String | GET request, returns response body |
| `http_post(url, headers, body)` | String | POST with headers map and body string |
| `http_request(method, url, headers, body)` | String | Any method: GET, POST, PUT, PATCH, DELETE. Use `""` for empty body. |

### Full Response (status + headers + body)

| Function | Returns | Description |
|----------|---------|-------------|
| `http_get_full(url)` | Map | `#{ status: 200, body: "...", headers: #{ "content-type": "..." } }` |
| `http_post_full(url, headers, body)` | Map | Same map structure |
| `http_request_full(method, url, headers, body)` | Map | Same map structure |

```rhai
// Simple POST to Slack
let headers = #{ "Authorization": "Bearer " + secret("SLACK_TOKEN"), "Content-Type": "application/json" };
let body = `{"channel": "#general", "text": "Hello from Krakiun!"}`;
http_post("https://slack.com/api/chat.postMessage", headers, body);

// Full response with status checking
let r = http_get_full("https://api.example.com/data");
if r.status == 200 {
    print("OK: " + r.body);
} else if r.status == 429 {
    print("Rate limited, retry after: " + r.headers["retry-after"]);
    wait(5);
}
```

---

## Todo / Kanban Board

| Function | Returns | Description |
|----------|---------|-------------|
| `todo_add(title, column)` | String | Add a task. Column name is case-insensitive. Returns confirmation. |
| `todo_items()` | String | Get all items (see [Return Formats](#return-formats)). Filter: `todo_items("To Do")` |
| `todo_columns()` | String | List all columns with item counts |
| `todo_done(id)` | String | Mark item as done by ID |
| `todo_move(id, column)` | String | Move item to another column by name |
| `todo_delete(id)` | String | Delete an item by ID |
| `todo_next()` | String | Get next task. Filter: `todo_next("To Do")` |

---

## Knowledge Base & RAG

| Function | Returns | Description |
|----------|---------|-------------|
| `kb_search(query)` | String | Semantic search across KB + conversations (see [Return Formats](#return-formats)). Default limit: 10. |
| `kb_search(query, limit)` | String | Same with custom result limit |
| `kb_index_text(title, content)` | String | Add text to KB. Auto-chunked (500 chars/chunk) and indexed. |

---

## Python Sandbox

```rhai
let result = python("print(2 ** 32)");                    // "4294967296"
let analysis = python("import json; data = [1,2,3]; print(sum(data))", 10); // timeout 10s
```

Requires Python 3 installed. Default timeout: 30s, max: 60s. The sandbox captures stdout — use `print()` in Python to return data.

---

## Provider Security

Control which AI providers your script can use:

```rhai
// Whitelist: only these providers allowed
allow_providers(["openai", "anthropic"]);

// Blacklist: block specific providers
block_providers(["ollama"]);

// After these calls, prompt() errors if it targets a blocked provider
let answer = prompt("ollama/llama3", "secret data"); // ERROR: Provider 'ollama' is blocked
```

Provider policies are **per-script** — they don't affect other running automations or the chat UI.

---

## Error Handling

All built-in functions that can fail throw catchable errors.

### Error Message Formats

| Source | Format | Example |
|--------|--------|---------|
| Permission denied | `"⛔ Tool 'name' is denied. Enable it in Settings > MCP Tools."` | `⛔ Tool 'execute_command' is denied.` |
| User denied | `"⛔ Permission denied by user for tool 'name'"` | `⛔ Permission denied by user for tool 'read_file'` |
| Tool execution error | `"❌ Error description"` | `❌ File not found: /tmp/missing.txt` |
| API key missing | `"❌ API key not configured. Add it in Settings > API Configuration."` | — |
| Provider blocked | `"Provider 'name' (model 'model') is blocked. Blocked: list"` | — |
| MCP server timeout | `"MCP server request timed out (30s)"` | — |
| Cancelled by user | `"Automation cancelled by user"` | — |

### Try/Catch Pattern

```rhai
try {
    let content = read_url("https://example.com/page");
    print(content);
} catch(err) {
    print("Failed: " + err);
}
```

### Retry with Backoff

```rhai
let result = "";
let attempts = 0;
while attempts < 3 {
    try {
        result = prompt("Explain quantum computing");
        break;
    } catch(err) {
        attempts += 1;
        print("Attempt " + attempts.to_string() + " failed: " + err);
        if attempts < 3 { wait(attempts * 2); } // 2s, 4s backoff
    }
}
```

### Cancellation Handling

Always re-throw cancellation errors — don't swallow them:

```rhai
try {
    let content = read_url(url);
} catch(error) {
    if error.to_string().contains("cancelled") {
        throw error; // Re-throw — let the automation stop
    }
    print("Non-fatal error: " + error);
}
```

---

## Debugging

### Available Tools

| Tool | How |
|------|-----|
| `print(value)` | Display any value in the automation timeline. Primary debugging tool. |
| `print(value.to_string())` | Force string conversion for non-string types |
| Validate button | Click "Validate" in the Rhai Editor to check for syntax errors before running |
| Timeline | All `print()`, tool starts, tool results, and errors appear in the chat timeline |
| Browser DevTools | `Cmd+Opt+I` (Mac) / `Ctrl+Shift+I` or `F12` (Windows/Linux) → Console tab shows `[Rhai]` prefixed logs |

### Debugging Patterns

```rhai
// Inspect variables
let data = web_search("topic", 3);
print("DEBUG data length: " + data.len().to_string());
print("DEBUG first 200 chars: " + data.sub_string(0, 200));

// Trace execution flow
print(">>> Step 1: Starting search");
let results = web_search(query, 5);
print(">>> Step 2: Got " + results.split("\n").len().to_string() + " lines");

// Inspect map contents
let m = #{ a: 1, b: "hello" };
print("Map keys: " + m.keys().to_string());

// Check types
let x = some_function();
print("Type check: is_string=" + x.is_string().to_string() + " len=" + x.len().to_string());
```

There is no step-through debugger, breakpoints, or log levels. `print()` is the only debugging mechanism. All output appears in the chat timeline in real-time.

---

## Limits & Quotas

### Engine Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Expression depth | Unlimited | `set_max_expr_depths(0, 0)` |
| String size | Unlimited | No max string length |
| Array size | Unlimited | No max array elements |
| Map size | Unlimited | No max map entries |
| Cancel check frequency | Every 256 operations | Engine checks cancellation flag |

### Function-Specific Limits

| Function | Limit | Details |
|----------|-------|---------|
| `prompt()` | No explicit token limit | Limited by provider's context window |
| `parallel_prompt()` | No explicit batch limit | All run concurrently. Practical limit ~20-30 before rate limiting. |
| `web_search()` | `max_results` capped by Tavily | Typical: 1-20 results |
| `read_file()` | No file size limit | Entire file loaded into memory as string |
| `save_file()` | No file size limit | Writes full content at once |
| `kb_index_text()` | No content size limit | Chunked at 500 chars each. Very large texts produce many chunks. |
| `kb_search()` | Max 2,000 conversation embeddings scanned | All KB embeddings scanned. Default limit: 10 results. |
| `ask_user()` | 600s default, 86400s (24h) max timeout | `0` or negative = 24h |
| `python()` | 60s max timeout | Default: 30s |
| `wait()` | No max | Checks cancellation every 200ms |
| Rhai tool handlers | 120s timeout | Automatically stopped |
| MCP server requests | 30s timeout | Per-request |

### Global Script Timeout

| Context | Timeout | Notes |
|---------|---------|-------|
| **Manual automation** (run from chat) | **No timeout** | Runs until completion, error, or user cancellation |
| **Rhai tool handler** (AI-called) | **120 seconds** | Automatically stopped |
| **Scheduled automation** | **No timeout** | Same as manual — runs until done or cancelled |

Manual automations and scheduled tasks have no global timeout. They run until they finish, throw an error, or are cancelled by the user. The only way to stop a runaway script is the stop button or killing the app.

### Rate Limiting

There are no built-in rate limits. Use `wait(1)` between consecutive API calls to avoid provider rate limits. For parallel operations, keep batch sizes reasonable (5-10 for web searches, 10-20 for prompts).

---

## Scheduling

Automations can run on a schedule (Settings > Scheduled Prompts):

| Schedule | Description |
|----------|-------------|
| **Hourly** | Every hour at minute 0 |
| **Daily** | At a specific hour (e.g., 8:00 AM) |
| **Weekly** | On a specific day and hour |
| **Monthly** | On a specific day of the month |
| **Custom** | Every N minutes (1-1440) |

**Note**: Scheduled tasks only run while the application is open. Max 3 concurrent scheduled tasks.

### Detecting Scheduled vs Manual Runs

When a script runs on schedule, `query` is empty. Use this to change behavior:

```rhai
let is_scheduled = query == "";

if is_scheduled {
    // Scheduled: use defaults
    let topic = "AI news";
    let results = web_search(topic, 5);
    let summary = prompt("Summarize: " + results);
    notify("Daily Digest", summary);
} else {
    // Manual: use user's input
    let results = web_search(query, 5);
    let summary = prompt("Summarize: " + results);
    print(summary);
}
```

### Dry Run Pattern

Test automations without side effects:

```rhai
let dry_run = secret("DRY_RUN") == "true";

let news = web_search("AI news today", 5);
let summary = prompt("Summarize:\n" + news);

if !dry_run {
    call_mcp("send_email_raw", #{ to: "team@company.com", subject: "Daily Digest", body: summary });
    notify("Email Sent", "Daily digest delivered");
} else {
    print("[DRY RUN] Would send email to team@company.com");
    print("[DRY RUN] Subject: Daily Digest");
    print("[DRY RUN] Body preview: " + truncate(summary, 200));
}
```

Set `DRY_RUN=true` in Settings > Automations > Secrets to enable.

### Note on `notify()` vs Other Communication

- `notify(title, message)` → **Telegram only** (requires bot token in Settings > API)
- For Slack: use `http_post_json()` with Slack webhook URL
- For email: use `call_mcp("send_email_raw", #{...})` (requires SMTP in Settings > Email)
- For Discord: use `http_post_json()` with Discord webhook URL

---

## Creating External MCP Servers

For tools that need to work across applications (not just Krakiun), create a standard MCP server. Krakiun supports two transport protocols:

### Transport: stdio (recommended for local tools)

The server runs as a subprocess. Krakiun communicates via stdin/stdout using JSON-RPC 2.0.

**Registration in Settings > MCP Servers > Add Server:**
```json
{
  "name": "My Tool Server",
  "transport": "stdio",
  "command": "/usr/local/bin/my-mcp-server",
  "args": ["--port", "0"],
  "env": { "MY_VAR": "value" }
}
```

### Transport: HTTP SSE (for remote servers)

The server exposes an HTTP endpoint. Krakiun sends JSON-RPC POST requests and reads SSE responses.

**Registration:**
```json
{
  "name": "Remote Server",
  "transport": "http_sse",
  "url": "https://api.example.com/mcp",
  "auth_token": "optional_bearer_token"
}
```

### Protocol Flow

1. Krakiun sends `initialize` (JSON-RPC) → server responds with capabilities
2. Krakiun sends `tools/list` → server responds with tool array
3. During chat, Krakiun sends `tools/call` with tool name + arguments → server responds with result

### Tool Definition Schema

Tools returned by `tools/list` must follow this format:

```json
{
  "tools": [
    {
      "name": "my_tool",
      "description": "What this tool does (shown to the AI)",
      "inputSchema": {
        "type": "object",
        "properties": {
          "param1": { "type": "string", "description": "First parameter" },
          "param2": { "type": "number", "description": "Optional number" }
        },
        "required": ["param1"]
      }
    }
  ]
}
```

The `inputSchema` is standard JSON Schema (draft-07). Krakiun passes it directly to the AI model for function calling.

### Tool Call Format

When the AI calls your tool, Krakiun sends:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "my_tool",
    "arguments": { "param1": "value1", "param2": 42 }
  }
}
```

Your server should respond:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "Tool result text here" }
    ]
  }
}
```

### Timeouts

- Request timeout: **30 seconds** per tool call
- Connection timeout: standard TCP timeouts

### Config Persistence

Server configurations are stored at `~/.local/share/com.krakiun.agent/mcp_servers.json` (Linux), `~/Library/Application Support/com.krakiun.agent/mcp_servers.json` (macOS), or `%APPDATA%\com.krakiun.agent\mcp_servers.json` (Windows).

### Minimal Python MCP Server Example

```python
#!/usr/bin/env python3
"""Minimal MCP Server — stdio transport, zero dependencies."""
import json, sys

def send(obj):
    text = json.dumps(obj)
    sys.stdout.write(f"Content-Length: {len(text)}\r\n\r\n{text}")
    sys.stdout.flush()

def read():
    headers = {}
    while True:
        line = sys.stdin.readline().strip()
        if not line: break
        k, v = line.split(": ", 1)
        headers[k] = v
    length = int(headers.get("Content-Length", 0))
    return json.loads(sys.stdin.read(length))

# Main loop
while True:
    msg = read()
    method = msg.get("method", "")
    id = msg.get("id")

    if method == "initialize":
        send({"jsonrpc": "2.0", "id": id, "result": {"capabilities": {"tools": {}}}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": id, "result": {"tools": [
            {"name": "hello", "description": "Say hello", "inputSchema": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Who to greet"}},
                "required": ["name"]
            }}
        ]}})
    elif method == "tools/call":
        name = msg["params"]["arguments"].get("name", "World")
        send({"jsonrpc": "2.0", "id": id, "result": {
            "content": [{"type": "text", "text": f"Hello, {name}!"}]
        }})
```

---

## Exporting & Distributing (.krakiun)

Export automations as protected binary files for distribution.

### How to Export

1. Open the automation in the Rhai Editor
2. Click **Export as .krakiun**
3. Save the file — this is your distributable binary

### How to Import

1. Go to Settings > Automations
2. Click **Import .krakiun**
3. The automation appears with a lock icon (protected)

### Protection Pipeline

| Stage | What Happens |
|-------|-------------|
| **1. Source to IR** | Rhai AST converted to intermediate representation. Source, comments, formatting discarded. |
| **2. Identifier mangling** | All variable/function names replaced with `_v0`, `_f1`, etc. Original names permanently lost. |
| **3. Control flow flattening** | Structured control flow → flat dispatcher with randomized block IDs |
| **4. Stack bytecode** | Compiled to proprietary stack-based instructions (PUSH, LOAD, JUMP, CALL) |
| **5. Encryption** | All strings AES-256-GCM encrypted (per-string keys). Instruction stream XOR-encoded. Opcodes remapped via random permutation. |
| **6. Integrity** | HMAC-SHA256 over entire file. Any modification detected and rejected. |

Each export produces a **different binary** even from identical source.

### Tips for Distributable Scripts

| Tip | Why |
|-----|-----|
| Use `prompt(text)` not `prompt(model, text)` | Buyers choose their own model |
| Use `secret("KEY")` for configurable values | Buyers set their own secrets |
| Use `ask_user()` for user-specific inputs | Don't hardcode values |
| Use `WORKING_DIR` for file paths | Each buyer has their own folder |
| Use `allow_providers(["openai", "anthropic"])` | Protect against local model interception |
| Test thoroughly before exporting | Bugs cannot be patched without re-export |

---

## Known Limitations

| Limitation | Details |
|-----------|---------|
| **No image/vision support** | `prompt()` accepts text only. Cannot send images to multimodal models from Rhai. Use the chat UI for vision tasks. |
| **No conversation history access** | Scripts cannot read the current conversation's messages. Use `kb_search()` to search across indexed conversations. |
| **No script-to-script calls** | One automation cannot invoke another directly. Use `store_set()`/`store_get()` for inter-script communication. |
| **No streaming** | `prompt()` waits for the full response. No token-by-token streaming in Rhai. |
| **No custom MCP server calls** | `call_mcp()` can only call built-in backend tools, not tools from custom MCP servers. |
| **Text-only prompts** | `prompt()` accepts and returns text only. Use `parse_json()` to convert JSON responses to structured Maps/Arrays. |
| **No versioning** | No API version number. Scripts are compatible with the installed Krakiun Agent version. |
| **Rhai tools are local** | `// TOOL:` definitions only work in Krakiun Agent. For cross-app tools, create an MCP Server. |
| **Scheduled tasks require app** | Tasks only run while Krakiun Agent is open. |

---

## Common Recipes

Frequently needed patterns for scripting:

### Parse JSON from an API

```rhai
let response = http_get("https://api.github.com/repos/rust-lang/rust");
let repo = parse_json(response);
print("Stars: " + repo["stargazers_count"].to_string());
print("Language: " + repo["language"]);
print("Description: " + repo["description"]);
```

### Build a URL with Query Parameters

```rhai
fn build_url(base, params) {
    let parts = [];
    for key in params.keys() {
        // Simple URL encoding for common chars
        let val = params[key].to_string()
            .replace(" ", "%20")
            .replace("&", "%26")
            .replace("=", "%3D");
        parts.push(key + "=" + val);
    }
    base + "?" + parts.reduce(|a, b| a + "&" + b, "")
}

let url = build_url("https://api.example.com/search", #{
    q: "rust async",
    page: 1,
    limit: 10
});
// https://api.example.com/search?q=rust%20async&page=1&limit=10
```

### POST JSON to a REST API

```rhai
let payload = #{ title: "New Post", body: "Content here", published: true };
let headers = #{
    "Authorization": "Bearer " + secret("API_TOKEN"),
    "Content-Type": "application/json"
};
let response = http_post("https://api.example.com/posts", headers, to_json(payload));
let result = parse_json(response);
print("Created post ID: " + result["id"].to_string());
```

### Extract Data with Regex

```rhai
// Extract all URLs from text
let urls = regex_match(text, r"https?://[^\s\)\"']+");

// Extract key=value pairs
let pairs = regex_match(config, r"(\w+)\s*=\s*(.+)");
// Returns: ["key1", "value1", "key2", "value2", ...]

// Extract numbers from text
let numbers = regex_match("Price: $42.50, Qty: 3", r"\d+\.?\d*");
// ["42.50", "3"]
```

### Escape Special Characters in JSON Strings

```rhai
fn json_escape(s) {
    s.replace("\\", "\\\\")
     .replace('"', '\\"')
     .replace("\n", "\\n")
     .replace("\r", "\\r")
     .replace("\t", "\\t")
}

let user_input = ask_user("Enter your message:");
let safe = json_escape(user_input);
let payload = `{"text": "` + safe + `"}`;
```

### Deduplicate with Hashing

```rhai
// Check if content has changed since last run
let content = http_get("https://example.com/status");
let current_hash = hash_sha256(content);
let previous_hash = store_get("status_hash");

if current_hash != previous_hash {
    print("Content changed! Processing...");
    store_set("status_hash", current_hash);
    // ... process new content
} else {
    print("No changes detected");
}
```

### Paginated API Requests

```rhai
let all_items = [];
let page = 1;
let has_more = true;

while has_more {
    let url = "https://api.example.com/items?page=" + page.to_string() + "&limit=50";
    let response = parse_json(http_get(url));
    let items = response["data"];

    for item in items {
        all_items.push(item["name"]);
    }

    has_more = items.len() == 50;  // Full page means there might be more
    page += 1;
    wait(1); // Rate limiting
}

print("Total items: " + all_items.len().to_string());
```

### Inspect Large Responses (Debugging)

```rhai
let response = http_get("https://api.example.com/large-data");
log("debug", "Response length: " + response.len().to_string());
log("debug", "First 500 chars: " + response.sub_string(0, 500));

// Pretty-print parsed JSON structure
let data = parse_json(response);
log("debug", "Keys: " + data.keys().to_string());
log("debug", "Items count: " + data["items"].len().to_string());

// Test with mock data (no API call)
// let mock = `{"status": "ok", "items": [{"id": 1}]}`;
// let data = parse_json(mock);
```

---

## Quick Reference Card

```
AI PROMPTING
  prompt(text)                    → String    Single prompt (user's model)
  prompt(model, text)             → String    Prompt specific model
  prompt_json(prompt, schema)     → Map       Force JSON response
  chat(messages)                  → String    Multi-turn conversation
  parallel_prompt(prompts)        → Array     Concurrent prompts

WEB & SEARCH
  web_search(query, max)          → String    Search (Tavily)
  web_search_json(query, max)     → Array     Search → [{title, url, snippet}]
  read_url(url)                   → String    Read page content (Jina)
  read_url_safe(url)              → String    Read page, "" on error
  parallel_web_search(queries)    → Array     Concurrent searches
  download_file(url, path)        → String    Download binary file

HTTP
  http_get(url)                   → String    GET → body
  http_post(url, headers, body)   → String    POST → body
  http_get_json(url)              → Map       GET + parse JSON
  http_post_json(url, hdrs, data) → Map       POST Map + parse JSON
  http_get_full(url)              → Map       GET → {status, body, headers}
  http_post_full(url, hdrs, body) → Map       POST → {status, body, headers}
  http_request(m, url, hdrs, b)   → String    Any method
  http_request_full(m, url, h, b) → Map       Any method → full response

FILES
  read_file(path)                 → String    Read file
  save_file(path, content)        → void      Write file
  append_file(path, content)      → void      Append to file
  file_exists(path)               → bool      Check existence
  list_files(path, pattern)       → Array     Glob match → file paths
  download_file(url, path)        → String    Download binary

JSON & DATA
  parse_json(text)                → Map/Array Parse JSON string
  to_json(value)                  → String    Value → JSON string
  extract_json(text)              → Map/Array Find JSON in text
  parse_csv(text)                 → Array     CSV → [{col: val}]
  to_csv(data)                    → String    [{col: val}] → CSV

TEXT
  extract_urls(text)              → Array     All URLs from text
  lines(text)                     → Array     Non-empty trimmed lines
  regex_match(text, pattern)      → Array     Regex matches/groups
  regex_replace(text, pat, repl)  → String    Regex replace all
  split_chunks(text, max)         → Array     Split at word boundaries
  strip_html(text)                → String    Remove HTML tags
  truncate(text, max)             → String    Truncate + "..."
  slugify(text)                   → String    "Hello World" → "hello-world"
  url_encode(text)                → String    URL-encode
  markdown_to_html(text)          → String    Markdown → HTML
  text_diff(old, new)             → String    Line diff (- / +)

ENCODING & HASHING
  base64_encode(text)             → String    Text → Base64
  base64_decode(text)             → String    Base64 → Text
  hash_sha256(text)               → String    SHA-256 hex
  hash_md5(text)                  → String    MD5 hex

ARRAYS
  unique(arr)                     → Array     Remove duplicates
  sort_by(arr, key)               → Array     Sort maps by field
  group_by(arr, key)              → Map       Group maps by field
  flatten(arr)                    → Array     Flatten one level
  chunk(arr, size)                → Array     Split into batches

STORAGE
  store_get(key)                  → String    Read value ("" if missing)
  store_set(key, value)           → void      Write value
  store_delete(key)               → void      Remove key
  store_increment(key)            → i64       Increment counter
  store_get_json(key)             → Map       Read structured data
  store_set_json(key, value)      → void      Write structured data
  cache_get(key, ttl)             → String    Read if within TTL
  cache_set(key, value)           → void      Write with timestamp

USER INTERACTION
  ask_user(question)              → String    Ask user (600s timeout)
  ask_user(question, timeout)     → String    Ask with custom timeout
  print(message)                  → void      Show in timeline
  log(level, message)             → void      Structured log (debug/info/warn/error)
  notify(title, message)          → void      Telegram notification

DATE & TIME
  timestamp()                     → String    Current "YYYY-MM-DD HH:MM:SS"
  date_add(ts, days)              → String    Add/subtract days
  date_diff(ts1, ts2)             → i64       Difference in seconds
  format_date(ts, format)         → String    Custom date format
  sleep_until(ts)                 → void      Wait until timestamp
  wait(seconds)                   → void      Pause (cancellable)

VALIDATION
  is_valid_email(text)            → bool      Email format check
  is_valid_url(text)              → bool      URL format check
  is_valid_json(text)             → bool      JSON validity check
  assert(cond, msg)               → void      Throw if false
  debounce(key, secs)             → bool      Rate limit check
  count_tokens(text)              → i64       Approximate token count

SYSTEM
  secret(key)                     → String    Read secret ("" if missing)
  require_secrets(keys)           → Map       Validate + get secrets
  working_dir()                   → String    Working folder path
  get_platform()                  → String    "macos"/"windows"/"linux"
  prompt_template(tpl, vars)      → String    ${key} interpolation
  render_template(tpl, vars)      → String    {{key}} interpolation (Mustache style)

HTML
  html_links(html)                → Array     Extract all href URLs
  html_text(html)                 → String    Strip tags, decode entities
  html_select(html, tag)          → Array     Inner text of matching tags
  strip_html(html)                → String    Same as html_text

MATH & STATISTICS
  round_to(val, decimals)         → Float     Round to N decimal places
  clamp(val, min, max)            → Number    Limit between bounds
  percentage_change(old, new)     → Float     ((new-old)/|old|) * 100
  stats_mean(arr)                 → Float     Arithmetic mean
  stats_median(arr)               → Float     Median value
  stats_sum(arr)                  → Float     Sum all numbers
  stats_min(arr)                  → Float     Minimum value
  stats_max(arr)                  → Float     Maximum value

ID & RANDOM
  uuid()                          → String    Random UUID v4
  short_id(length)                → String    Random alphanumeric string
  random_int(min, max)            → i64       Random integer in range
  random_float()                  → f64       Random float 0.0-1.0

CRYPTO
  hmac_sha256(key, message)       → String    HMAC-SHA256 hex digest

STRING CASE
  title_case(text)                → String    "hello world" → "Hello World"
  snake_case(text)                → String    "HelloWorld" → "hello_world"
  camel_case(text)                → String    "hello_world" → "helloWorld"
  pascal_case(text)               → String    "hello_world" → "HelloWorld"
  kebab_case(text)                → String    "HelloWorld" → "hello-world"

STRING FORMATTING
  pad_left(text, width, char)     → String    Left-pad to width
  pad_right(text, width, char)    → String    Right-pad to width
  repeat_str(text, count)         → String    Repeat N times
  word_count(text)                → i64       Count words
  format_number(num, decimals)    → String    1234567 → "1,234,567"
  to_hex(num)                     → String    255 → "ff"
  from_hex(text)                  → i64       "ff" → 255
  url_decode(text)                → String    "%20" → " "

PATHS
  path_join(parts)                → String    Cross-platform path join
  path_basename(path)             → String    "/a/b/file.txt" → "file.txt"
  path_dirname(path)              → String    "/a/b/file.txt" → "/a/b"
  path_extension(path)            → String    "file.txt" → "txt"
  file_size(path)                 → i64       File size in bytes
  env_var(name)                   → String    Read OS environment variable
  temp_dir()                      → String    System temp directory

ARRAYS EXTENDED
  zip(arr1, arr2)                 → Array     Combine into [a, b] pairs
  enumerate_arr(arr)              → Array     Add indices: [[0, val], ...]
  range(start, end)               → Array     [start, ..., end-1]
  range_step(start, end, step)    → Array     With custom step
  reverse(arr)                    → Array     Reversed copy
  intersect(arr1, arr2)           → Array     Common elements
  difference(arr1, arr2)          → Array     In arr1 but not arr2
  keys(map)                       → Array     Map keys
  values(map)                     → Array     Map values
  entries(map)                    → Array     [[key, val], ...]

DATE ADVANCED
  day_name(ts)                    → String    "Monday", "Tuesday", etc.
  month_name(ts)                  → String    "January", "February", etc.
  today()                         → String    Current date at midnight
  now()                           → String    Current timestamp (alias)
  is_business_day(date)           → bool      Mon-Fri check
  next_business_day(date)         → String    Next Mon-Fri

CONFIG FORMATS
  yaml_parse(text)                → Map       Parse YAML to Map/Array
  yaml_stringify(value)           → String    Value → YAML string
  toml_parse(text)                → Map       Parse TOML to Map
  toml_stringify(value)           → String    Value → TOML string

EXTRACTORS
  extract_emails(text)            → Array     All email addresses
  extract_numbers(text)           → Array     All numbers (incl. decimals)
  extract_phone_numbers(text)     → Array     Phone numbers (7+ digits)

FILES EXTENDED
  dir_exists(path)                → bool      Check if directory exists
  copy_file(src, dest)            → String    Copy file
  create_dir(path)                → void      Create directory (+ parents)
  delete_dir(path)                → void      Delete directory recursively
  file_modified_at(path)          → String    Last modified timestamp

AUTH & SECURITY
  basic_auth_header(user, pass)   → String    "Basic base64(user:pass)"
  jwt_decode(token)               → Map       Decode JWT claims (no verify)
  oauth2_token(id, secret, url, scope) → Map  Get OAuth2 token
  json_diff(obj1, obj2)           → Map       {added, removed, changed}

IMAGES
  image_to_base64(path)           → String    Image → data:...;base64,...
  image_from_base64(b64, path)    → String    Base64 → image file

ENCRYPTION
  encrypt(data, password)         → String    AES-256-GCM encrypt → base64
  decrypt(encrypted, password)    → String    Decrypt → original text

ASSERTIONS
  assert_eq(v1, v2, msg?)        → void      Throw if not equal
  expect(value, msg?)             → Dynamic   Throw if () (null)
  hmac_verify(key, data, sig)     → bool      Verify HMAC-SHA256 signature

FORMATTERS
  format_bytes(n)                 → String    1234567 → "1.2 MB"
  format_duration(secs)           → String    3661 → "1h 1m 1s"
  word_wrap(text, width)          → String    Wrap at word boundaries
  normalize_text(text)            → String    Lowercase + strip diacritics

ARRAYS ADVANCED
  unique_by(arr, field)           → Array     Deduplicate by field
  count_by(arr, field)            → Map       Frequency count
  min_by(arr, field)              → Dynamic   Min by field
  max_by(arr, field)              → Dynamic   Max by field
  sliding_window(arr, size)       → Array     Overlapping windows

NETWORK
  dns_lookup(hostname)            → String    Resolve to IP
  port_check(host, port)          → bool      TCP port open check
  http_health_check(url)          → Map       {ok, status, latency_ms}
  graphql_query(url, q, vars, h)  → Map       Execute GraphQL query
  rss_parse(url_or_xml)           → Array     Parse RSS/Atom feed

MCP BRIDGE
  call_mcp(tool, params)          → String    Call any MCP tool
  (see MCP Tools Bridge section for full tool list)

EXTERNAL
  python(code)                    → String    Python sandbox (30s default)
  python(code, timeout)           → String    Python with custom timeout
```

---

## Rhai Gotchas

Common pitfalls that will bite every new user:

### Integer Division

```rhai
let x = 5 / 2;      // 2 (NOT 2.5!) — integer division
let x = 5.0 / 2.0;  // 2.5 — float division
let x = 5 / 2.0;    // 2.5 — mixed promotes to float
```

**Rule**: If both operands are integers, result is integer. Use `.0` on at least one operand for float division.

### Strings Are Immutable

```rhai
let s = "hello";
s += " world";   // OK — creates new string, reassigns
s.push(' ');      // ERROR — strings don't have push()

// Use concatenation:
let s = s + " suffix";
```

### Arrays and Maps Copy by Value

```rhai
let a = [1, 2, 3];
let b = a;          // b is a COPY, not a reference
b.push(4);
print(a.len());     // 3 — a is unchanged!

// Same for maps:
let m1 = #{ x: 1 };
let m2 = m1;
m2["x"] = 99;
print(m1["x"]);     // 1 — m1 is unchanged
```

### `len()` Counts Bytes, Not Characters

```rhai
let s = "café";
s.len();    // 5 (UTF-8 bytes), not 4 characters

// For character count, use:
let char_count = s.chars().count();  // 4
```

### For Loop Consumes the Array

```rhai
let arr = [1, 2, 3];
for x in arr {
    // x is a copy of each element
    // modifying x does NOT modify arr
}
// arr is still [1, 2, 3] and accessible
```

### Closures Don't Capture Variables Automatically

```rhai
let x = 42;
let f = |a| a + x;  // ERROR: x is not captured

// Workaround: pass as parameter
let f = |a, ctx| a + ctx;
f(1, x);  // 43
```

### No Null — Use `()` (Unit)

```rhai
let x = ();         // Rhai's "null" equivalent
if x.type_of() == "()" {
    print("x is empty");
}

// Functions that return nothing return ()
let result = print("hello");  // result is ()
```

### String-to-Number Conversion Can Fail

```rhai
"abc".to_int();   // Throws error, doesn't return 0!

// Safe pattern:
let n = if is_valid_json(text) { text.to_int() } else { 0 };
```

---

## Troubleshooting & FAQ

### "AI returns empty string"

**Causes**: Model API timeout, empty API key, provider rate limit, or model doesn't exist.

```rhai
let key = secret("OPENAI_KEY");
assert(key != "", "OpenAI key not configured");

let result = prompt("Hello");
if result == "" {
    log("warn", "Empty AI response — check API key and model availability");
}
```

### "store_get() returns ()"

`store_get()` returns `""` (empty string), not `()`. If you see `()`, you're using `store_get_json()` with a missing key.

```rhai
let val = store_get("my_key");
if val == "" { print("Key not found"); }  // Correct

let data = store_get_json("my_key");
if data.type_of() == "()" { print("Key not found"); }  // For JSON store
```

### "Script runs forever"

Check for: infinite `loop {}` without `break`, `wait()` with very large number, or `while` condition that never becomes false.

```rhai
// Always add a safety counter:
let attempts = 0;
while !done {
    attempts += 1;
    if attempts > 100 { break; }
    // ... your logic
}
```

### "Variable not found"

Variables are block-scoped. A variable declared inside `if`, `for`, or `{}` is not visible outside.

```rhai
// WRONG:
if true { let x = 5; }
print(x);  // ERROR: x not found

// RIGHT:
let x = 0;
if true { x = 5; }
print(x);  // 5
```

### "Python sandbox can't find library X"

The sandbox has Python stdlib only. For pip packages, they auto-install if available but Docker must be running. Check:

```rhai
let status = call_mcp("execute_command", #{ command: "docker info" });
print(status);  // Should show Docker info, not an error
```

### "Permission denied for tool X"

Tool permissions are set in Settings > MCP Tools. Check: is the tool set to "Deny"? Is the folder in the allowed folders list?

### "Timeout waiting for user response"

`ask_user()` defaults to 600 seconds (10 minutes). For longer waits:

```rhai
let answer = ask_user("Take your time:", 0);  // 0 = 24h max
```

---

## Design Patterns

### Polling Pattern

Check a condition at intervals until it's met:

```rhai
// Wait for a deployment to complete
let max_checks = 30;
let check_interval = 10;  // seconds

for i in range(0, max_checks) {
    let status = http_get_json("https://api.example.com/deploy/123");
    if status["state"] == "completed" {
        print("Deploy finished!");
        break;
    }
    if status["state"] == "failed" {
        print("Deploy failed: " + status["error"]);
        break;
    }
    print("Check " + (i + 1).to_string() + "/" + max_checks.to_string() + ": " + status["state"]);
    wait(check_interval);
}
```

### ETL Pattern (Extract → Transform → Load)

```rhai
// Extract: read data from source
let csv_data = read_file("input.csv");
let rows = parse_csv(csv_data);

// Transform: process each row
let processed = [];
for row in rows {
    if is_valid_email(row["email"]) {
        row["name"] = row["name"].to_upper();
        row["domain"] = regex_match(row["email"], r"@(.+)")[0];
        processed.push(row);
    }
}

// Load: write to destination
save_file("output.csv", to_csv(processed));
print("Processed " + processed.len().to_string() + " valid rows");
```

### Fan-Out Pattern

Distribute work across parallel prompts:

```rhai
let urls = extract_urls(web_search("topic", 10));
let contents = [];
for url in urls { contents.push(read_url_safe(url)); }

// Fan out: analyze each page in parallel
let prompts = [];
for c in contents {
    if c.len() > 100 {
        prompts.push("Extract key facts from:\n" + truncate(c, 3000));
    }
}
let analyses = parallel_prompt(prompts);

// Fan in: combine results
let combined = analyses.reduce(|a, b| a + "\n---\n" + b, "");
let report = prompt("Synthesize these analyses into a report:\n" + combined);
save_file("report.md", report);
```

### Cache + Debounce Pattern

Avoid redundant API calls:

```rhai
if !debounce("price_check", 300) {
    print("Checked too recently, skipping");
    return;
}

let cached_price = cache_get("product_price", 600);
if cached_price != "" {
    print("Using cached price: " + cached_price);
} else {
    let price = http_get_json("https://api.store.com/product/123")["price"].to_string();
    cache_set("product_price", price);

    let old_price = store_get("last_known_price");
    if old_price != "" && old_price != price {
        notify("Price Changed", "Was: " + old_price + " → Now: " + price);
    }
    store_set("last_known_price", price);
}
```

---

## Limitations & Workarounds

| Limitation | Workaround |
|-----------|------------|
| No module imports | Use `python()` for complex libraries. Or split logic across `call_mcp` tools. |
| No closures in registered functions | Use `parallel_prompt()` instead of `parallel_map()`. Build prompt arrays manually. |
| No streaming from `prompt()` | Use `print()` for progress. `prompt()` returns full response when done. |
| No image input to `prompt()` | Use the chat UI for vision. Or `download_file()` + `python()` for image processing. |
| No true concurrency in loops | Use `parallel_prompt()` or `parallel_web_search()` for parallel work. |
| `len()` counts bytes not chars | Use `s.chars().count()` for character count in non-ASCII text. |
| Integer division truncates | Add `.0` to at least one operand: `5.0 / 2` → `2.5`. |
| No regex named groups | Use numbered groups and index into the flat array returned by `regex_match()`. |
| No WebSocket support | Use polling pattern with `http_get()` + `wait()`. |
| Can't access conversation history | Use `kb_search()` to search across indexed conversations. |

---

## Best Practices

1. **Use `prompt(text)` over `prompt(model, text)`** — let users choose their model
2. **Use `wait(1)` between API calls** — avoid rate limits
3. **Use `try/catch` around network calls** — handle failures gracefully
4. **Use `secret("KEY")` for sensitive values** — never hardcode API tokens
5. **Set a Working Folder** in automation settings — predictable `save_file`/`read_file` location
6. **Use `print()` for progress** — users see what's happening in the timeline
7. **Re-throw cancellation errors** — don't swallow `"cancelled"` in catch blocks
8. **Use `parallel_prompt()` when possible** — concurrent queries for independent tasks
9. **Validate `ask_user()` responses** — users might type unexpected input
10. **Keep tool descriptions specific** — the AI uses them to decide when to call your tool

---

## Complete Examples

### Example 1: Quick Summary

```rhai
// Complexity: Beginner
// Requires: web_search, prompt
// Estimated runtime: ~15s

let results = web_search(query, 5);
let summary = prompt(
    "Summarize the following search results about: " + query
    + "\n\nResults:\n" + results
    + "\n\nWrite a concise 3-paragraph summary."
);
print(summary);
save_file("summary.md", summary);
```

### Example 2: Interactive Research

```rhai
// Complexity: Intermediate
// Requires: web_search, read_url, ask_user, prompt
// Estimated runtime: ~60s (includes user interaction)

let focus = ask_user("What aspect of '" + query + "' interests you most?");
print("Researching: " + query + " (focus: " + focus + ")");

let results1 = web_search(query + " " + focus, 5);
wait(1);
let results2 = web_search(query + " latest news", 3);

// Read the top result in full
let url = "";
for line in results1.split("\n") {
    if line.starts_with("http") { url = line.trim(); break; }
}

let full_page = "";
if url != "" {
    try { full_page = read_url(url); } catch {}
}

let report = prompt(
    "Write a detailed report about: " + query
    + "\nUser focus: " + focus
    + "\n\nSearch results:\n" + results1
    + "\n\nAdditional results:\n" + results2
    + "\n\nFull article:\n" + full_page
    + "\n\nStructure: Executive Summary, Key Findings, Details, Sources."
);

print(report);
save_file("research_report.md", report);
```

### Example 3: Content Translator

```rhai
// Complexity: Beginner
// Requires: read_file, prompt
// Estimated runtime: ~30s per language

let content = read_file(query);
let languages = ["Spanish", "French", "German"];

for lang in languages {
    print("Translating to " + lang + "...");
    let translated = prompt(
        "Translate the following text to " + lang
        + ". Keep the original formatting.\n\n" + content
    );
    save_file(lang.to_lower() + "_translation.md", translated);
    print("Saved: " + lang.to_lower() + "_translation.md");
    wait(1);
}
print("All translations complete!");
```

### Example 4: AI-Callable Code Reviewer Tool

```rhai
// Complexity: Intermediate
// Requires: call_mcp (read_file), prompt
// Estimated runtime: ~20s per file

// TOOL: review_code
// DESCRIPTION: Review source code for bugs, security issues, and improvements
// PARAM: path (string, required) — Path to the source file to review
// PARAM: focus (string, optional) — What to focus on: security, performance, readability
// HANDLER: handle_review_code

fn handle_review_code(args) {
    let code = call_mcp("read_file", #{ path: args["path"] });
    let focus = if args.contains("focus") { args["focus"] } else { "bugs, security, and code quality" };

    prompt(
        "Review this code. Focus on: " + focus + ".\n"
        + "For each issue: line number, severity, description, fix.\n\n"
        + "File: " + args["path"] + "\n\n```\n" + code + "\n```"
    )
}
```

### Example 5: Slack Integration with Error Handling

```rhai
// Complexity: Intermediate
// Requires: web_search, prompt, secret, http_post_full, store_increment
// Estimated runtime: ~20s

allow_providers(["openai", "anthropic"]); // Security: no local model leaks

let news = web_search(query + " latest developments", 5);
let summary = prompt("Create a 3-bullet executive summary:\n" + news);

// Post to Slack
let token = secret("SLACK_TOKEN");
if token == "" {
    print("Error: Set SLACK_TOKEN in Settings > Automations > Secrets");
} else {
    let headers = #{ "Authorization": "Bearer " + token, "Content-Type": "application/json" };
    let payload = `{"channel": "` + secret("SLACK_CHANNEL") + `", "text": "` + summary.replace('"', '\\"') + `"}`;

    let r = http_post_full("https://slack.com/api/chat.postMessage", headers, payload);
    if r.status == 200 {
        print("Posted to Slack successfully");
    } else {
        print("Slack error (" + r.status.to_string() + "): " + r.body);
    }
}

// Track execution
let runs = store_get("slack_post_count");
store_set("slack_post_count", (if runs == "" { 0 } else { runs.to_int() } + 1).to_string());
```

### Example 6: WordPress Auto-Publisher

```rhai
// Complexity: Advanced
// Requires: web_search, read_url, prompt, secret, base64_encode, http_post_full, parse_json, to_json, notify
// Estimated runtime: ~2-3 minutes

// Automated blog post generator + WordPress publisher
// Set these secrets in Settings > Automations > Secrets:
//   WP_URL       → https://yourblog.com
//   WP_USER      → your_wordpress_username
//   WP_APP_PASS  → WordPress Application Password (Users > Profile > Application Passwords)

let wp_url = secret("WP_URL");
let wp_user = secret("WP_USER");
let wp_pass = secret("WP_APP_PASS");

if wp_url == "" || wp_user == "" || wp_pass == "" {
    print("Error: Set WP_URL, WP_USER, WP_APP_PASS in Settings > Automations > Secrets");
    throw "WordPress credentials not configured";
}

// Step 1: Research the topic
print("Researching: " + query);
let research = web_search(query, 8);
wait(1);

// Read top 2 sources for depth
let sources = [];
let urls_found = 0;
for line in research.split("\n") {
    if line.starts_with("http") && urls_found < 2 {
        try {
            let content = read_url(line.trim());
            sources.push(content.sub_string(0, 3000));
            urls_found += 1;
        } catch {}
        wait(1);
    }
}

// Step 2: Generate the blog post
let article = prompt(
    "Write a professional blog post about: " + query + "\n\n"
    + "Requirements:\n"
    + "- 800-1200 words\n"
    + "- Include an engaging introduction\n"
    + "- Use H2 and H3 headings (HTML: <h2>, <h3>)\n"
    + "- Include practical examples\n"
    + "- End with a conclusion and call-to-action\n"
    + "- Write in HTML format (not markdown)\n\n"
    + "Research sources:\n" + research + "\n\n"
    + "Detailed sources:\n" + sources.reduce(|a, b| a + "\n---\n" + b, "")
);

// Step 3: Generate title and excerpt
let title = prompt("Generate a compelling SEO-friendly blog title (max 60 chars, no quotes) for:\n" + query);
let excerpt = prompt("Write a 150-character meta description for this article:\n" + article.sub_string(0, 500));

// Step 4: Publish to WordPress via REST API
let auth = base64_encode(wp_user + ":" + wp_pass);
let headers = #{
    "Authorization": "Basic " + auth,
    "Content-Type": "application/json"
};

let post_data = to_json(#{
    title: title,
    content: article,
    excerpt: excerpt,
    status: "draft",   // Change to "publish" for auto-publish
    categories: [],
    tags: []
});

let r = http_post_full(wp_url + "/wp-json/wp/v2/posts", headers, post_data);

if r.status == 201 {
    let result = parse_json(r.body);
    let post_url = result["link"];
    print("Published draft: " + post_url);
    notify("WordPress", "New draft: " + title);

    // Save locally too
    save_file("wordpress_" + timestamp() + ".html", article);
} else {
    log("error", "WordPress API error (" + r.status.to_string() + "): " + r.body.sub_string(0, 300));
    print("Failed to publish. Saving locally...");
    save_file("failed_post_" + timestamp() + ".html", "<h1>" + title + "</h1>\n" + article);
}
```

---

### Example 7: Full-Stack Data Pipeline (Uses Modern Functions)

```rhai
// Complexity: Advanced
// Requires: yaml_parse, rss_parse, parse_csv, group_by, count_by, sort_by,
//           prompt_json, to_csv, format_number, format_bytes, debounce, cache_get/set
// Estimated runtime: ~2 minutes

// ETL pipeline: RSS feeds → AI analysis → CSV report → email
//
// Requires pipeline_config.yml in working folder:
//   feeds:
//     - https://blog.rust-lang.org/feed.xml
//     - https://hnrss.org/frontpage
//   max_articles: 20

if !debounce("data_pipeline", 1800) {
    print("Pipeline ran recently, skipping");
    return;
}

let creds = require_secrets(["SMTP_EMAIL", "REPORT_RECIPIENT"]);

// Step 1: Load config from YAML
let config = yaml_parse(read_file("pipeline_config.yml"));
let feeds = config["feeds"];  // Array of RSS feed URLs
let max_articles = config["max_articles"];

// Step 2: Fetch all RSS feeds
print("Fetching " + feeds.len().to_string() + " RSS feeds...");
let all_articles = [];
for feed_url in feeds {
    let cached = cache_get("feed_" + hash_md5(feed_url), 3600);
    if cached != "" {
        let items = parse_json(cached);
        for item in items { all_articles.push(item); }
    } else {
        let items = rss_parse(feed_url);
        cache_set("feed_" + hash_md5(feed_url), to_json(items));
        for item in items { all_articles.push(item); }
    }
    wait(1);
}
print("Total articles: " + all_articles.len().to_string());

// Step 3: Deduplicate and sort
let unique_articles = unique_by(all_articles, "url");
let sorted = sort_by(unique_articles, "date");
let recent = reverse(sorted);
let trimmed = [];
for i in range(0, if recent.len() < max_articles { recent.len() } else { max_articles }) {
    trimmed.push(recent[i]);
}
let recent = trimmed;

// Step 4: AI analysis — extract structured data from each article
let analyzed = [];
let batches = chunk(recent, 5);
for batch in batches {
    let prompts = [];
    for article in batch {
        prompts.push(
            "Analyze this article and return JSON: {\"category\": \"tech|business|science|other\", \"sentiment\": \"positive|neutral|negative\", \"summary\": \"one sentence\"}\n\n"
            + "Title: " + article["title"] + "\n" + article["content"]
        );
    }
    let results = parallel_prompt(prompts);
    for i in range(0, results.len()) {
        if !results[i].starts_with("ERROR:") {
            let analysis = extract_json(results[i]);
            let row = #{
                title: batch[i]["title"],
                url: batch[i]["url"],
                date: batch[i]["date"],
                category: analysis["category"],
                sentiment: analysis["sentiment"],
                summary: analysis["summary"]
            };
            analyzed.push(row);
        }
    }
    wait(2);
}

// Step 5: Generate statistics
let by_category = count_by(analyzed, "category");
let by_sentiment = count_by(analyzed, "sentiment");

let stats_report = "## Pipeline Report — " + today() + "\n\n";
stats_report += "Articles analyzed: " + analyzed.len().to_string() + "\n\n";
stats_report += "### By Category\n";
for cat in entries(by_category) {
    stats_report += "- " + title_case(cat[0]) + ": " + cat[1].to_string() + "\n";
}
stats_report += "\n### By Sentiment\n";
for sent in entries(by_sentiment) {
    stats_report += "- " + title_case(sent[0]) + ": " + sent[1].to_string() + "\n";
}

// Step 6: Save CSV report
save_file("report_" + slugify(today()) + ".csv", to_csv(analyzed));
save_file("report_" + slugify(today()) + ".md", stats_report);

// Step 7: Send email summary
let html_report = markdown_to_html(stats_report);
call_mcp("send_email_raw", #{
    to: creds["REPORT_RECIPIENT"],
    subject: "Data Pipeline Report — " + format_date(now(), "%A %B %d"),
    body: html_report
});

print(stats_report);
let run = store_increment("pipeline_runs");
log("info", "Pipeline run #" + run.to_string() + " complete");
```

---

*Krakiun Agent — Build, automate, and distribute AI-powered workflows.*
