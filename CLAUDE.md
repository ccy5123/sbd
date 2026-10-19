# Session rules (set by the user)

- **First message of every new session: say whether this session is a cloud session or a local one** (e.g. "이 세션은
  클라우드 세션입니다 (claude.ai 컨테이너)" / "이 세션은 로컬 세션입니다 (사용자 컴퓨터)"), and repeat it whenever a
  session is resumed or teleported. `claude --teleport` makes a separate copy; the cloud original keeps running, so
  say which copy the user is talking to. Only a local session can reach the company server over SSH.
- **Never subscribe to, watch or schedule check-ins on pull requests** (no PR activity subscriptions, no send_later or
  scheduled re-checks), even when a PR is created.
- Reply in Korean. Clarify each question before answering; ask with AskUserQuestion, recommended option first.
- Read `HANDOFF.md` first (status, plan, working rules).
