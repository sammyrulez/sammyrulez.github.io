---
title: "Running Gemma 4 31B on an Apple Silicon Mac with Ollama"
date: 2026-04-26 22:48
tags:
- AI
- LLM
- MCP
- Python
category: blog
author: samreghenzi
description:  "Look ma no tokens"
---


## A practical configuration for a 32 GB M5 Mac that still needs to remain usable

Running large language models locally has become surprisingly practical on Apple Silicon. With a modern Mac, Ollama, and a carefully quantized GGUF model, it is possible to run models that only a short time ago would have felt out of reach for a personal machine.

This post collects the practical findings from configuring **Gemma 4 31B** on a **32 GB Apple Silicon Mac with an M5 processor**, using Ollama and a highly compressed GGUF quantization.

The goal is not to squeeze every last token per second out of the machine. The goal is more realistic:

> Run a capable 31B local model while keeping the Mac usable for normal work: browser, IDE, terminal, notes, chat apps, and light development tools.

That distinction matters. A configuration that works for a benchmark is not necessarily a configuration you want to live with all day.

---

## The model

The model used in this setup is:

```text
gemma-4-31B-it-UD-IQ3_XXS.gguf
```

This is an aggressively quantized GGUF build of Gemma 4 31B. The `IQ3_XXS` quantization makes the model small enough to fit into machines that would otherwise be unable to run a 31B model at all.

The trade-off is obvious: this is not the highest quality quantization, but it gives access to a much larger model class on consumer hardware.

The Ollama `Modelfile` starts from the local GGUF file:

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf
```

---

## Understanding the main Ollama parameters

Before tuning the configuration, it helps to understand what the key parameters actually control.

### `num_ctx`

`num_ctx` controls the maximum context window used by the model.

A larger context means the model can keep more conversation, documents, code, or instructions in memory. But it also increases memory usage, especially through the KV cache.

For this model, useful values are:

```text
6144   conservative
8192   balanced
12288  aggressive
```

For daily use on a 32 GB Mac, `8192` is a good target.

---

### `num_batch`

`num_batch` affects how many tokens are processed together during prompt ingestion.

It mostly impacts the speed at which the model reads the input prompt, not necessarily the speed at which it generates the answer token by token.

Higher values can improve responsiveness with longer prompts, but they also increase temporary memory pressure.

Good values for this setup are:

```text
32   conservative
64   balanced
96   aggressive
```

For a daily driver configuration, `64` is a reasonable compromise. If the Mac becomes sluggish or the runner crashes, this is one of the first values to reduce.

---

### `num_gpu`

In Ollama, `num_gpu` does not mean “number of GPUs”. It means how many model layers are offloaded to the GPU.

For Gemma 4 31B, the theoretical maximum is:

```text
num_gpu 60
```

because the model has 60 layers.

However, full offload is not always the best practical choice. On a machine that must remain usable for other work, leaving some margin is often better than maximizing GPU offload.

For a 32 GB M5 Mac, a good range is:

```text
50   conservative
55   balanced
60   aggressive / full offload
```

The recommended daily value is `55`.

---

## The recommended daily configuration

This is the configuration I would use as a balanced daily driver.

It gives a useful context window, keeps prompt processing reasonably fast, and avoids pushing the system too close to the edge.

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 8192
PARAMETER num_batch 64
PARAMETER num_gpu 55

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
```

Create or replace the model with:

```bash
cd ~/ollama-models/gemma4-31b-iq3

cat > Modelfile <<'EOF'
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 8192
PARAMETER num_batch 64
PARAMETER num_gpu 55

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
EOF

ollama stop gemma4-31b-iq3xxs-32gb
ollama rm gemma4-31b-iq3xxs-32gb
ollama create gemma4-31b-iq3xxs-32gb -f ./Modelfile
```

Then test it:

```bash
ollama run gemma4-31b-iq3xxs-32gb "Write a Python hello world."
```

---

## Environment variables

For this setup, Flash Attention and quantized KV cache are useful.

If using the Ollama macOS app, set the variables with `launchctl`:

```bash
launchctl setenv OLLAMA_FLASH_ATTENTION "1"
launchctl setenv OLLAMA_KV_CACHE_TYPE "q8_0"
launchctl setenv OLLAMA_CONTEXT_LENGTH "8192"
launchctl setenv OLLAMA_KEEP_ALIVE "5m"
```

Then quit and reopen Ollama from the menu bar.

If running Ollama manually from the terminal:

```bash
OLLAMA_FLASH_ATTENTION=1 \
OLLAMA_KV_CACHE_TYPE=q8_0 \
OLLAMA_CONTEXT_LENGTH=8192 \
OLLAMA_KEEP_ALIVE=5m \
ollama serve
```

---

## What `OLLAMA_KV_CACHE_TYPE=q8_0` does

The KV cache stores the internal attention state for tokens that have already been processed. It grows with the active context length.

Using:

```bash
OLLAMA_KV_CACHE_TYPE=q8_0
```

asks Ollama to store the KV cache in an 8-bit quantized format.

The practical effect is:

```text
lower memory usage
better support for longer context windows
usually minimal quality loss compared to f16 KV cache
```

It is especially useful when running large models with larger context windows.

However, it does not significantly reduce the memory used by the model weights themselves. It mainly helps with memory used by context.

For this reason, `q8_0` is useful, but it is not a magic fix for every memory issue.

---

## Flash Attention

Flash Attention should be enabled when using quantized KV cache:

```bash
OLLAMA_FLASH_ATTENTION=1
```

It helps reduce memory usage and can improve efficiency with larger contexts.

For this model, I would keep it enabled.

---

## Keeping the Mac usable

Apple Silicon uses unified memory. The CPU and GPU share the same memory pool.

That means a local LLM can directly compete with everything else on the Mac:

```text
browser tabs
IDE
Docker
database containers
video calls
Slack or Teams
file indexing
other development tools
```

This is why the best configuration is not necessarily the most aggressive one.

The aim is to leave enough headroom that the system does not constantly swap or become unresponsive.

---

## Wired memory limit

Some users increase the Metal wired memory limit with:

```bash
sudo sysctl iogpu.wired_limit_mb=22000
```

On a 32 GB Mac, I would use one of these values:

```text
20000  conservative workstation mode
22000  balanced daily mode
24000  LLM-priority mode
```

For daily work, I would start with:

```bash
sudo sysctl iogpu.wired_limit_mb=22000
```

I would avoid pushing this too close to total system memory. Values like 28000 or 30000 may help a benchmark but can make the machine unpleasant to use for normal work.

---

## Three practical profiles

### 1. Workstation profile

Use this when you also need Docker, an IDE, many browser tabs, or other heavy tools.

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 6144
PARAMETER num_batch 32
PARAMETER num_gpu 50

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
```

Recommended environment:

```bash
sudo sysctl iogpu.wired_limit_mb=20000

launchctl setenv OLLAMA_FLASH_ATTENTION "1"
launchctl setenv OLLAMA_KV_CACHE_TYPE "q8_0"
launchctl setenv OLLAMA_CONTEXT_LENGTH "6144"
launchctl setenv OLLAMA_KEEP_ALIVE "2m"
```

This is the safest profile for a Mac that must remain responsive.

---

### 2. Balanced daily profile

This is the recommended default.

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 8192
PARAMETER num_batch 64
PARAMETER num_gpu 55

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
```

Recommended environment:

```bash
sudo sysctl iogpu.wired_limit_mb=22000

launchctl setenv OLLAMA_FLASH_ATTENTION "1"
launchctl setenv OLLAMA_KV_CACHE_TYPE "q8_0"
launchctl setenv OLLAMA_CONTEXT_LENGTH "8192"
launchctl setenv OLLAMA_KEEP_ALIVE "5m"
```

This is the profile I would use most of the time.

---

### 3. LLM-priority profile

Use this when the Mac is mostly dedicated to local inference.

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 12288
PARAMETER num_batch 96
PARAMETER num_gpu 60

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
```

Recommended environment:

```bash
sudo sysctl iogpu.wired_limit_mb=24000

launchctl setenv OLLAMA_FLASH_ATTENTION "1"
launchctl setenv OLLAMA_KV_CACHE_TYPE "q8_0"
launchctl setenv OLLAMA_CONTEXT_LENGTH "12288"
launchctl setenv OLLAMA_KEEP_ALIVE "10m"
```

This is more aggressive. It may be useful for focused LLM sessions, but I would not use it while doing normal development work.

---

## How to verify what is happening

After running the model, check:

```bash
ollama ps
```

This shows whether the model is loaded and how it is using the available processors.

To inspect logs:

```bash
grep -iE "offload|layers|gpu|metal|memory" ~/.ollama/logs/server.log | tail -n 80
```

Look for messages indicating how many layers were offloaded to the GPU.

For example:

```text
offloaded 55/60 layers to GPU
```

That confirms that `num_gpu 55` is actually being applied.

---

## Troubleshooting instability

If Ollama crashes or the Mac becomes sluggish, reduce parameters in this order.

First reduce `num_batch`:

```text
64 -> 32
```

Then reduce `num_ctx`:

```text
8192 -> 6144
```

Then reduce `num_gpu`:

```text
55 -> 50
```

Finally reduce the wired memory limit:

```text
22000 -> 20000
```

A stable machine is more useful than a theoretical maximum configuration that crashes during real work.

---

## About Metal crashes

During experimentation, one possible failure mode is a Metal backend crash, with logs similar to:

```text
ggml-metal-device.m:608: GGML_ASSERT([rsets->data count] == 0) failed
panic during panic
```

When this happens, it is often better to reset the setup rather than keep pushing the same configuration.

A practical recovery sequence is:

```bash
killall Ollama
killall ollama

launchctl unsetenv OLLAMA_FLASH_ATTENTION
launchctl unsetenv OLLAMA_KV_CACHE_TYPE
launchctl unsetenv OLLAMA_CONTEXT_LENGTH

sudo sysctl iogpu.wired_limit_mb=20000
```

Then reboot the Mac and restart from a conservative profile.

---

## Final recommendation

For a 32 GB M5 Mac that should remain useful as a normal workstation, I would use this:

```bash
sudo sysctl iogpu.wired_limit_mb=22000

launchctl setenv OLLAMA_FLASH_ATTENTION "1"
launchctl setenv OLLAMA_KV_CACHE_TYPE "q8_0"
launchctl setenv OLLAMA_CONTEXT_LENGTH "8192"
launchctl setenv OLLAMA_KEEP_ALIVE "5m"
```

And this `Modelfile`:

```text
FROM ./gemma-4-31B-it-UD-IQ3_XXS.gguf

PARAMETER num_ctx 8192
PARAMETER num_batch 64
PARAMETER num_gpu 55

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER top_k 64
```

This is not the most extreme configuration. It is the one I would actually want to use.

It gives enough context for serious work, enough GPU offload for acceptable performance, and enough memory headroom to keep the Mac usable while doing other things.

That is usually the sweet spot for local LLMs: not maximum throughput, but sustainable performance.
