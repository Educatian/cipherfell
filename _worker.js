// Cipherfell — keyless adaptive AI tutor. Pages "advanced mode": routes the whole
// project; static is served via env.ASSETS. The browser never holds a key.
// Backends tried in order: (1) Cloudflare Workers AI binding `AI` (free tier),
// (2) HuggingFace Inference (free token in secret `HF_TOKEN`). If neither is
// configured, /api/tutor returns empty text and the game falls back to scripted hints.
const HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"; // non-gated, served on HF free router

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/tutor" && request.method === "POST") {
      try {
        const body = await request.json();
        const concept = String(body.concept || "security thinking").slice(0, 140);
        const mistake = String(body.mistake || "the learner is stuck").slice(0, 240);
        const ko = body.lang === "ko";
        const system =
          "You are a warm, concise tutor inside a medieval-village cybersecurity learning game called Cipherfell. " +
          "Give ONE short formative hint (at most two sentences) that nudges the learner toward the security idea " +
          "WITHOUT revealing the puzzle's answer. Keep the game's gentle, encouraging tone. " +
          (ko ? "Reply in natural Korean." : "Reply in English.");
        const user = `Security concept: ${concept}. Situation: ${mistake}. Give a gentle hint, not the solution.`;
        const messages = [{ role: "system", content: system }, { role: "user", content: user }];

        // (1) Cloudflare Workers AI binding
        if (env.AI) {
          try {
            const out = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", { messages, max_tokens: 110 });
            const text = (out && (out.response || out.result || "")) || "";
            if (String(text).trim()) return json({ text: String(text).trim(), via: "workers-ai" });
          } catch (e) {}
        }
        // (2) HuggingFace Inference (free token in secret HF_TOKEN)
        if (env.HF_TOKEN) {
          try {
            const r = await fetch("https://router.huggingface.co/v1/chat/completions", {
              method: "POST",
              headers: { authorization: "Bearer " + env.HF_TOKEN, "content-type": "application/json" },
              body: JSON.stringify({ model: HF_MODEL, messages, max_tokens: 110, temperature: 0.6 }),
            });
            const j = await r.json();
            const text = (j && j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content) || "";
            if (String(text).trim()) return json({ text: String(text).trim(), via: "huggingface" });
          } catch (e) {}
        }
        return json({ text: "" });
      } catch (e) {
        return json({ text: "" });
      }
    }
    return env.ASSETS.fetch(request);
  },
};
function json(o) { return new Response(JSON.stringify(o), { headers: { "content-type": "application/json" } }); }
