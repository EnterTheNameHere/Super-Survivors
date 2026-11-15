
function isModEnabled(modname)

	local activatedMods = getActivatedMods();
	for i=0, activatedMods:size()-1, 1 do
		if activatedMods:get(i) == modname then
			return true;
		end
	end
	return false;
end


function getSaveDir()
	local relative = getWorld():getGameMode():toString() .. getFileSeparator() .. getWorld():getWorld()
	return getAbsoluteSaveFolderName(relative) .. getFileSeparator()
end

function getSourceSquareOfItem(item,character)

	if (item.getWorldItem ~= nil) and (item:getWorldItem() ~= nil) then
		return item:getWorldItem():getSquare()		
	elseif(item:getContainer() ~= nil) then
		return item:getContainer():getSourceGrid()
	end
	
	return character:getCurrentSquare()
	
end
