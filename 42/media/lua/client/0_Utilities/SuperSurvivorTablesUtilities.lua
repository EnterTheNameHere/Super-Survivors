-- Non-persistence table helper. World data is owned by SSPersistence.
function table.randFrom( t )
	local keys = {}

	for key, value in pairs(t) do
		keys[#keys+1] = key --Store keys in another table
	end

	local key = ZombRand(1, #keys)
	return keys[key]
end
