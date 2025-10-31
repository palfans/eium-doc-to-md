--[[
Pandoc Lua Filter for HTML to Markdown Conversion

This Lua filter is used by Pandoc to process HTML elements during conversion
to GitHub Flavored Markdown. It handles special cases that require custom
processing beyond standard HTML-to-Markdown conversion.

Features:
  - Converts command synopsis divs to code blocks
  - Rewrites HTML links to Markdown links (.html -> .md)
  - Removes attributes from code blocks for cleaner output
  - Unwraps span elements to simplify structure
  - Filters out specific background images

Usage:
  pandoc --from=html --to=gfm --lua-filter=html_to_md.lua input.html -o output.md
]]--

local utils = require 'pandoc.utils'

-- Check if an element has a specific CSS class
-- @param attr: The element's attributes table
-- @param class: The class name to check for
-- @return: Boolean indicating if the class is present
local function has_class(attr, class)
  if not attr or not attr.classes then
    return false
  end
  for _, c in ipairs(attr.classes) do
    if c == class then
      return true
    end
  end
  return false
end

-- Process Div elements
-- Converts divs with class 'cmdsynopsis' to code blocks with cleaned content
-- All other divs are unwrapped, keeping only their content
-- @param el: The Div element to process
-- @return: CodeBlock for cmdsynopsis divs, otherwise the div's content
function Div(el)
  if has_class(el.attr, 'cmdsynopsis') then
    -- Convert the div content to plain text
    local text = utils.stringify(el)
    -- Normalize whitespace: replace multiple spaces with single space
    text = text:gsub('%s+', ' ')
    -- Trim leading whitespace
    text = text:gsub('^%s+', '')
    -- Trim trailing whitespace
    text = text:gsub('%s+$', '')
    -- Return as a code block for better formatting
    return pandoc.CodeBlock(text)
  end
  -- For all other divs, return just the content (unwrap the div)
  return el.content
end

-- Process Link elements
-- Rewrites internal HTML links to Markdown links
-- Removes all link attributes for cleaner output
-- @param el: The Link element to process
-- @return: Modified Link element with updated target and no attributes
function Link(el)
  -- Only process internal links (those without URL schemes like http:, https:)
  if el.target and not el.target:match('^%a[%w+.-]*:') then
    -- Replace .html with .md, preserving query strings (?...)
    el.target = el.target:gsub('%.html(%?.*)$', '.md%1')
    -- Replace .html with .md, preserving fragment identifiers (#...)
    el.target = el.target:gsub('%.html(#.*)$', '.md%1')
    -- Replace standalone .html extensions
    el.target = el.target:gsub('%.html$', '.md')
  end
  -- Remove all attributes from links for cleaner Markdown
  el.attributes = {}
  return el
end

-- Process CodeBlock elements
-- Removes all attributes (classes, identifiers) from code blocks
-- This results in plain fenced code blocks without language specifications
-- @param el: The CodeBlock element to process
-- @return: CodeBlock with cleared attributes
function CodeBlock(el)
  if pandoc and pandoc.Attr then
    -- Create a new empty Attr object (cleaner approach)
    el.attr = pandoc.Attr()
  else
    -- Fallback: manually clear attributes
    el.attributes = {}
    el.identifier = ''
    el.classes = {}
  end
  return el
end

-- Process Span elements
-- Unwraps all span elements, returning only their content
-- This simplifies the output by removing unnecessary inline containers
-- @param el: The Span element to process
-- @return: The span's content without the wrapper
function Span(el)
  return el.content
end

-- Process Image elements
-- Filters out specific images that shouldn't appear in the Markdown output
-- @param el: The Image element to process
-- @return: Empty table to remove the image, or the original element to keep it
function Image(el)
  -- Remove the background index image
  if el.src == 'image/background_index.png' then
    return {}
  end
  -- Keep all other images
  return el
end
