/* Keep Sphinx's asynchronous search summaries total.

   Search.makeSearchSummary() deliberately returns null when a result target
   has no usable prose.  Sphinx 8.2's caller nevertheless passes that value to
   appendChild(), producing one console error per such result.  Preserve the
   stock search and highlighting behavior while representing an empty summary
   by an empty inline node. */
if (typeof Search !== "undefined" && Search.makeSearchSummary) {
  const makeSearchSummary = Search.makeSearchSummary.bind(Search);
  Search.makeSearchSummary = (...arguments_) =>
    makeSearchSummary(...arguments_) ?? document.createElement("span");
}

/* Keep the Pagefind search useful across result navigation.

   Fragment links do not unload the current page, so close the dialog before
   following every result.  A release-scoped session value also restores the
   query after cross-page navigation.  When the dialog opens, select that
   query so the next typed character starts a replacement search. */
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("pagefind-modal");
  const dialog = modal?.querySelector("dialog");
  const input = modal?.querySelector('input[type="search"]');
  if (!modal || !dialog || !input) return;

  const contentRoot = new URL(
    document.documentElement.dataset.content_root,
    location.href,
  ).pathname;
  const storageKey = `mpg-search:${contentRoot}`;

  const readQuery = () => {
    try {
      return sessionStorage.getItem(storageKey) ?? "";
    } catch {
      return "";
    }
  };
  const writeQuery = (query) => {
    try {
      if (query) sessionStorage.setItem(storageKey, query);
      else sessionStorage.removeItem(storageKey);
    } catch {
      // Search remains functional when storage is unavailable.
    }
  };

  input.addEventListener("input", () => writeQuery(input.value));
  const restoredQuery = readQuery();
  if (restoredQuery) {
    input.value = restoredQuery;
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }

  modal.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target?.closest(".pf-result-link")) return;
    writeQuery(input.value);
    if (dialog.open) dialog.close();
  });

  const selectQuery = () => {
    if (!dialog.open) return;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      input.focus();
      input.select();
    }));
  };
  new MutationObserver(selectQuery).observe(dialog, {
    attributes: true,
    attributeFilter: ["open"],
  });
});
