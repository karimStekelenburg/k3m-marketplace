[Skip to main content](https://code.claude.com/docs/en/context-window#content-area)

[Claude Code Docs home page![light logo](https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/logo/light.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=78fd01ff4f4340295a4f66e2ea54903c)![dark logo](https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/logo/dark.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=1298a0c3b3a1da603b190d0de0e31712)](https://code.claude.com/docs/en/overview)

![US](https://d3gk2c5xim1je2.cloudfront.net/flags/US.svg)

English

Search...

Ctrl KAsk AI

- [Claude Developer Platform](https://platform.claude.com/)
- [Claude Code on the Web](https://claude.ai/code)
- [Claude Code on the Web](https://claude.ai/code)

Search...

Navigation

Core concepts

Explore the context window

[Getting started](https://code.claude.com/docs/en/overview) [Build with Claude Code](https://code.claude.com/docs/en/sub-agents) [Deployment](https://code.claude.com/docs/en/third-party-integrations) [Administration](https://code.claude.com/docs/en/setup) [Configuration](https://code.claude.com/docs/en/settings) [Reference](https://code.claude.com/docs/en/cli-reference) [Resources](https://code.claude.com/docs/en/legal-and-compliance)

##### Getting started

- [Overview](https://code.claude.com/docs/en/overview)
- [Quickstart](https://code.claude.com/docs/en/quickstart)
- [Changelog](https://code.claude.com/docs/en/changelog)

##### Core concepts

- [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory)
- [Explore the context window](https://code.claude.com/docs/en/context-window)

##### Use Claude Code

- [Store instructions and memories](https://code.claude.com/docs/en/memory)
- [Permission modes](https://code.claude.com/docs/en/permission-modes)
- [Common workflows](https://code.claude.com/docs/en/common-workflows)
- [Best practices](https://code.claude.com/docs/en/best-practices)

##### Platforms and integrations

- [Overview](https://code.claude.com/docs/en/platforms)
- [Remote Control](https://code.claude.com/docs/en/remote-control)
- Claude Code on the web

- Claude Code on desktop

- [Chrome extension (beta)](https://code.claude.com/docs/en/chrome)
- [Visual Studio Code](https://code.claude.com/docs/en/vs-code)
- [JetBrains IDEs](https://code.claude.com/docs/en/jetbrains)
- Code review & CI/CD

- [Claude Code in Slack](https://code.claude.com/docs/en/slack)

Core concepts

# Explore the context window

Copy page

An interactive simulation of how Claude Code’s context window fills during a session. See what loads automatically, what each file read costs, and when rules and hooks fire.

Copy page

Claude Code’s context window holds everything Claude knows about your session: your instructions, the files it reads, its own responses, and content that never appears in your terminal. The timeline below walks through what loads and when. See [the written breakdown](https://code.claude.com/docs/en/context-window#what-the-timeline-shows) for the same content as a list.

This interactive timeline works best on a larger screen. See [the written breakdown below](https://code.claude.com/docs/en/context-window#what-the-timeline-shows) for the same concepts.

Explore the context window

A simulated session showing what enters context and what it costs

~0tokens

/ 200K · illustrative

System

CLAUDE.md

Memory

Skills

MCP

Rules

You

Files

Output

Claude

Hooks

= appears in your terminal

$claude

▶Start session

Watch what loads into context, from the moment you run `claude` through a full conversation.

👁

Hover or click any event

Hover to preview. Click to pin so you can scroll.

Key takeaway

A lot loads before you type anything. CLAUDE.md, memory, skills, and MCP tools are all in context before your first prompt.

In your terminal you see

The input box, waiting for your first message. Everything above loads silently before you type anything.

▶

0%⛶

## [​](https://code.claude.com/docs/en/context-window\#what-the-timeline-shows)  What the timeline shows

The session walks through a realistic flow with representative token counts:

- **Before you type anything**: CLAUDE.md, auto memory, MCP tool names, and skill descriptions all load into context. Your own setup may add more here, like an [output style](https://code.claude.com/docs/en/output-styles) or text from [`--append-system-prompt`](https://code.claude.com/docs/en/cli-reference), which both go into the system prompt the same way.
- **As Claude works**: each file read adds to context, [path-scoped rules](https://code.claude.com/docs/en/memory#path-specific-rules) load automatically alongside matching files, and a [PostToolUse hook](https://code.claude.com/docs/en/hooks-guide) fires after each edit.
- **The follow-up prompt**: a [subagent](https://code.claude.com/docs/en/sub-agents) handles the research in its own separate context window, so the large file reads stay out of yours. Only the summary and a small metadata trailer come back.
- **At the end**: `/compact` replaces the conversation with a structured summary. Most startup content reloads automatically. The [skill](https://code.claude.com/docs/en/skills) listing is the one exception.

## [​](https://code.claude.com/docs/en/context-window\#check-your-own-session)  Check your own session

The visualization uses representative numbers. To see your actual context usage at any point, run `/context` for a live breakdown by category with optimization suggestions. Run `/memory` to check which CLAUDE.md and auto memory files loaded at startup.

## [​](https://code.claude.com/docs/en/context-window\#related-resources)  Related resources

For deeper coverage of the features shown in the timeline, see these pages:

- [Extend Claude Code](https://code.claude.com/docs/en/features-overview): when to use CLAUDE.md vs skills vs rules vs hooks vs MCP
- [Store instructions and memories](https://code.claude.com/docs/en/memory): CLAUDE.md hierarchy and auto memory
- [Subagents](https://code.claude.com/docs/en/sub-agents): delegate research to a separate context window
- [Best practices](https://code.claude.com/docs/en/best-practices): managing context as your primary constraint
- [Reduce token usage](https://code.claude.com/docs/en/costs#reduce-token-usage): strategies for keeping context usage low

Was this page helpful?

YesNo

[Explore the .claude directory](https://code.claude.com/docs/en/claude-directory) [Store instructions and memories](https://code.claude.com/docs/en/memory)

Ctrl+I

[Claude Code Docs home page![light logo](https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/logo/light.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=78fd01ff4f4340295a4f66e2ea54903c)![dark logo](https://mintcdn.com/claude-code/c5r9_6tjPMzFdDDT/logo/dark.svg?fit=max&auto=format&n=c5r9_6tjPMzFdDDT&q=85&s=1298a0c3b3a1da603b190d0de0e31712)](https://code.claude.com/docs/en/overview)

[x](https://x.com/AnthropicAI) [linkedin](https://www.linkedin.com/company/anthropicresearch)

Company

[Anthropic](https://www.anthropic.com/company) [Careers](https://www.anthropic.com/careers) [Economic Futures](https://www.anthropic.com/economic-futures) [Research](https://www.anthropic.com/research) [News](https://www.anthropic.com/news) [Trust center](https://trust.anthropic.com/) [Transparency](https://www.anthropic.com/transparency)

Help and security

[Availability](https://www.anthropic.com/supported-countries) [Status](https://status.anthropic.com/) [Support center](https://support.claude.com/)

Learn

[Courses](https://www.anthropic.com/learn) [MCP connectors](https://claude.com/partners/mcp) [Customer stories](https://www.claude.com/customers) [Engineering blog](https://www.anthropic.com/engineering) [Events](https://www.anthropic.com/events) [Powered by Claude](https://claude.com/partners/powered-by-claude) [Service partners](https://claude.com/partners/services) [Startups program](https://claude.com/programs/startups)

Terms and policies

[Privacy choices](https://code.claude.com/docs/en/context-window#) [Privacy policy](https://www.anthropic.com/legal/privacy) [Disclosure policy](https://www.anthropic.com/responsible-disclosure-policy) [Usage policy](https://www.anthropic.com/legal/aup) [Commercial terms](https://www.anthropic.com/legal/commercial-terms) [Consumer terms](https://www.anthropic.com/legal/consumer-terms)

Assistant

Responses are generated using AI and may contain mistakes.