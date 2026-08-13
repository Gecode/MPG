-- Keep the SVG web asset but select the sibling PDF for LaTeX output.
if FORMAT:match("latex") then
  function Image(image)
    image.src = image.src:gsub("%.svg$", ".pdf")
    return image
  end
end
