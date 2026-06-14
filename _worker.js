// Cipherfell — keyless adaptive AI tutor via Cloudflare Workers AI.
// Pages "advanced mode": this routes the whole project; static is served via env.ASSETS.
// Requires a Workers AI binding named `AI` on the Pages project (Settings → Functions → AI bindings).
// If the binding is absent, /api/tutor returns empty text and the game falls back to scripted hints.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/tutor" && request.method === "POST") {
      try {
        const body = await request.json();
        const concept = String(body.concept || "security thinking").slice(0, 140);
        const mistake = String(body.mistake || "the learner is stuck").slice(0, 240);
        const ko = body.lang === "ko";
        if (!env.AI) return Response.json({ text: "" });
        const system =
          "You are a warm, concise tutor inside a medieval-village cybersecurity learning game called Cipherfell. " +
          "Give ONE short formative hint (at most two sentences) that nudges the learner toward the security idea " +
          "WITHOUT revealing the puzzle's answer. Keep the game's gentle, encouraging tone. " +
          (ko ? "Reply in natural Korean." : "Reply in English.");
        const user = `Security concept: ${concept}. Situation: ${mistake}. Give a gentle hint, not the solution.`;
        const out = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
          messages: [{ role: "system", content: system }, { role: "user", content: user }],
          max_tokens: 110,
        });
        const text = (out && (out.response || out.result || "")) || "";
        return Response.json({ text: String(text).trim() });
      } catch (e) {
        return Response.json({ text: "" });
      }
    }
    return env.ASSETS.fetch(request);
  },
};
