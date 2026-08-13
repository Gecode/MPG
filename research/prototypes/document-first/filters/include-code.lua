-- Replace an empty code block carrying include="path" with that file's text.
function CodeBlock(block)
  local filename = block.attributes.include
  if filename == nil then
    return nil
  end

  local file, message = io.open(filename, "r")
  if file == nil then
    error("cannot include code file " .. filename .. ": " .. message)
  end
  block.text = file:read("*a")
  file:close()
  block.attributes.include = nil
  block.attributes["data-source-file"] = filename
  return block
end
