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
