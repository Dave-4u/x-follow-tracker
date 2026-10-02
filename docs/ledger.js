/* Follow Ledger core: pure functions shared by the page and node tests. */
(function (root) {
  const idx = (users) => new Map(users.filter((u) => u && u.id != null).map((u) => [String(u.id), u]));

  function compare(following, followers, previousFollowers) {
    const fing = idx(following), fers = idx(followers);
    const notBack = following.filter((u) => !fers.has(String(u.id)));
    const fans = followers.filter((u) => !fing.has(String(u.id)));
    const mutuals = following.filter((u) => fers.has(String(u.id)));
    const unfollowed = previousFollowers && previousFollowers.length ? previousFollowers.filter((u) => !fers.has(String(u.id))) : [];
    const newFollowers = previousFollowers && previousFollowers.length ? (() => { const p = idx(previousFollowers); return followers.filter((u) => !p.has(String(u.id))); })() : [];
    return { notBack, fans, mutuals, unfollowed, newFollowers };
  }

  // Accepts: tracker snapshot {kind, users:[...]}, a plain [{id,username,name}] array,
  // or X data-archive files (following.js / follower.js: window.YTD.following.part0 = [...]).
  function parseFile(name, text) {
    let kind = null;
    const t = text.trim();
    if (/^window\.YTD\./.test(t)) {
      kind = /YTD\.following/.test(t) ? "following" : "followers";
      const arr = JSON.parse(t.slice(t.indexOf("=") + 1));
      const users = arr.map((row) => {
        const v = row.following || row.follower || {};
        return { id: String(v.accountId), username: "", name: "", link: v.userLink || `https://x.com/i/user/${v.accountId}` };
      });
      return { kind, users, source: "X archive" };
    }
    const data = JSON.parse(t);
    if (Array.isArray(data)) {
      kind = /follower/i.test(name) && !/following/i.test(name) ? "followers" : /following/i.test(name) ? "following" : null;
      return { kind, users: data, source: name };
    }
    return { kind: data.kind || null, users: data.users || [], source: name, savedAt: data.saved_at, username: data.username };
  }

  function toCSV(users) {
    const q = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
    return ["id,username,name", ...users.map((u) => [u.id, u.username, u.name].map(q).join(","))].join("\n");
  }

  const api = { compare, parseFile, toCSV };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.Ledger = api;
})(typeof window !== "undefined" ? window : globalThis);
