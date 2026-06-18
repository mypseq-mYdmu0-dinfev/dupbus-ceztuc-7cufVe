set conversionFolder to POSIX file "/Volumes/FURY 2TB/Fury Documents/PDF Conversion" as alias
set timeStamp to do shell script "date +%Y%m%d%H%M"
set outputFolderPath to (conversionFolder as text) & timeStamp & ":"

tell application "Finder"
	if not (exists folder outputFolderPath) then
		make new folder at conversionFolder with properties {name:timeStamp}
	end if
end tell

set outputFolder to alias outputFolderPath
set convertedFiles to {} -- Track successfully converted files

-- Get all files except the script itself
tell application "Finder"
	set allFiles to every file of conversionFolder whose name is not "PDF Conversion.scpt"
end tell

if allFiles is {} then
	display dialog "No files to convert found." buttons {"OK"} default button 1
	return
end if

repeat with f in allFiles
	set theFile to (f as alias)

	tell application "Finder"
		set fileName to name of f
		set fileExt to name extension of f
	end tell

	-- Get base name without extension
	set AppleScript's text item delimiters to "."
	set nameItems to text items of fileName
	set AppleScript's text item delimiters to ""

	if (count of nameItems) > 1 then
		set baseName to (items 1 thru -2 of nameItems) as text
		set AppleScript's text item delimiters to "."
		set baseName to baseName as text
		set AppleScript's text item delimiters to ""
	else
		set baseName to fileName
	end if

	set pdfName to baseName & ".pdf"
	set pdfPath to ((outputFolder as text) & pdfName)

	tell application "Finder"
		if not (exists file pdfPath) then
			-- Handle different file types
			set conversionSuccess to false

			if fileExt is "pages" then
				tell application "Pages"
					set theDoc to open theFile
					export theDoc to file pdfPath as PDF
					close theDoc saving no
				end tell
				set conversionSuccess to true

			else if fileExt is "numbers" then
				tell application "Numbers"
					set theDoc to open theFile
					export theDoc to file pdfPath as PDF
					close theDoc saving no
				end tell
				set conversionSuccess to true

			else if fileExt is "key" then
				tell application "Keynote"
					set theDoc to open theFile
					export theDoc to file pdfPath as PDF
					close theDoc saving no
				end tell
				set conversionSuccess to true

			else if fileExt is "docx" or fileExt is "doc" then
				tell application "Microsoft Word"
					set theDoc to open file name (theFile as text)
					save as theDoc file format format PDF file name pdfPath
					close theDoc saving no
				end tell
				set conversionSuccess to true

			else if fileExt is "xlsx" or fileExt is "xls" then
				tell application "Microsoft Excel"
					open (theFile as text)
					set theDoc to active workbook
					save workbook as theDoc filename pdfPath file format PDF file format
					close theDoc saving no
				end tell
				set conversionSuccess to true

			else if fileExt is "pptx" or fileExt is "ppt" then
				tell application "Microsoft PowerPoint"
					open theFile
					set theDoc to active presentation
					save theDoc in pdfPath as save as PDF
					close theDoc saving no
				end tell
				set conversionSuccess to true
			end if

			-- Add to converted files list if successful
			if conversionSuccess then
				set end of convertedFiles to theFile
			end if
		end if
	end tell
end repeat

delay 1

-- Tag PDFs: remove red tags and add green tags
tell application "Finder"
	set pdfFiles to every file of outputFolder whose name extension is "pdf"
	repeat with pdfFile in pdfFiles
		set thePOSIXPath to POSIX path of (pdfFile as alias)
		try
			-- Remove all existing tags first, then add green tag
			do shell script "xattr -d com.apple.metadata:_kMDItemUserTags " & quoted form of thePOSIXPath & " 2>/dev/null; xattr -w com.apple.metadata:_kMDItemUserTags '<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"><plist version=\"1.0\"><array><string>Green\n6</string></array></plist>' " & quoted form of thePOSIXPath
		end try
	end repeat
end tell

-- Delete original files after successful conversions
tell application "Finder"
	repeat with originalFile in convertedFiles
		try
			delete originalFile
		end try
	end repeat
end tell

display dialog "Conversion completed. Original files deleted." buttons {"OK"} default button 1