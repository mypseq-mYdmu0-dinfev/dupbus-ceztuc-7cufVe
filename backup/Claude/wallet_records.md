I need help processing my shopping records into a standardised table format. Here are the specific requirements:

1. Data Cleansing:
- Remove all special characters (^, #, *)
- Each complete record should be consolidated into a single line, even if originally spread across multiple lines
- A complete record typically consists of:
  * Item description
  * Quantity/weight information
  * Unit price (if present)
  * Final price (always in decimal format)

2. Format Standardization:
- Remove spaces between quantity and unit (e.g., "0.832 kg" → "0.832kg")
- Remove the word "NET"
- Remove space between @ and price (e.g., "@ $4.70/kg" → "@$4.70/kg")
- For "each" units, shorten to "ea" (remove "ch")
- For "Qty", replace with "x" followed immediately by number (e.g., "Qty 2" → "x2")
- Use title case (e.g., "DOVE SHMP DAILY CARE 850ML" → "Dove Shampoo Daily Care 850ml")
- Separate if lowercase followed by uppercase (e.g., "OliveOil" → "Olive Oil")
- For multiple identical items, ensure to add unit price (e.g., "ABC x 3 ... $3" → "ABC x3 @$1ea") and combine into single line if not already (e.g., 3 lines of "ABC ... $1" → combine as "ABC x3 @$1ea")
- For pack units:
  * Remove "pk"
  * Add "x" before the number without space
  * Indicate pack amount (e.g., "12pk" → "x12 x1pk")
  * If Qty is specified for packs, update accordingly (e.g., "12pk Qty 2" → "x12 x2pk")
- For special deal discounts:
  * Calculate the effective unit price by dividing final price by quantity
  * Combine item and discount into single line showing effective price
  * Example: "Item x2 @$5.00ea ... $10.00" with "Deal ... -$3.00" becomes "Item x2 @$3.50ea ... $7.00"
- For litre units, use capital "L" (e.g., "1l" → "1L")
- Examples:
  * "JW Mackerel Fillets In OliveOil 125g Qty 2 @ $4.20 each" means I bought 2 units, so mark it as "JW Mackerel Fillets In OliveOil 125g x2 @$4.20ea"
  * "Wholemeal Rolls 6pk" means I bought 1 unit but it has 6/pack, so mark it as "Wholemeal Roll x6 x1pk"

3. Output Format:
- Create a table in an artifact with two columns:
  * First column header: "Note"
  * Second column header: "Amount"
- First column should contain the complete item description including quantity and unit price
- Second column should contain only the final price
- Example format:
  * Note: "Potato Red Washed Lse 0.832kg @$4.70/kg"
  * Amount: "3.91"

Example of raw input:
```
Potato Red Washed Lse
0.832 kg NET @ $4.70/kg
3.91
```

Example of processed output:
| Note | Amount |
|------|---------|
| Potato Red Washed Lse 0.832kg @$4.70/kg | 3.91 |

I'll provide the raw shopping records and you'll process them according to these specifications
.
below is an example of raw records:
Potato Red Washed Lse
0.832 kg NET @ $4.70/kg
3.91
Kiwifruit Gold Imported
0.547 kg NET @ $10.50/kg
5.74
Peach White Flat Md
0.477 kg NET @ $6.90/kg
3.29
Nongshim Noodles Neo Guri 5x120g Pack
8.00
Woolworths Free Range Eggs 700g 12pk
Qty 2 @ $6.10 each
12.20
Mccain Hash Browns Shredded 750g
5.80
^#Sanpellegrino Sparklmineral Water 1l
2.95
^Bibigo Mandu Pork & KimchiDumplings 280g
6.00
Don Bacon Pansize Double Smoked 200g
6.60
^WW Salmon Portions Skin On 280g
13.00
WW Cold Smoked Salmon 100g
5.95
Diced Beef Casserole 500g
11.00
Pork Rashers Medium
10.96
Woolworths Lamb Extra Trim Cutlets
27.51
WW Extra Virgin Olive Oil Spray 150g
3.70
Asparagus Mini
3.50
#Bakery Du Jour Brioche Loaf 450g
4.50
Blueberry 170g
2.00
Berry Strawberry Premium 300g
4.50
.
below is an example of processed records:
| Note | Amount |
|------|---------|
| Potato Red Washed Lse 0.832kg @$4.70/kg | 3.91 |
| Kiwifruit Gold Imported 0.547kg @$10.50/kg | 5.74 |
| Peach White Flat Md 0.477kg @$6.90/kg | 3.29 |
| Nongshim Noodles Neo Guri x5 x1pk | 8.00 |
| Woolworths Free Range Eggs 700g x12 x2pk @$6.10ea | 12.20 |
| Mccain Hash Browns Shredded 750g | 5.80 |
| Sanpellegrino Sparklmineral Water 1L | 2.95 |
| Bibigo Mandu Pork & KimchiDumplings 280g | 6.00 |
| Don Bacon Pansize Double Smoked 200g | 6.60 |
| WW Salmon Portions Skin On 280g | 13.00 |
| WW Cold Smoked Salmon 100g | 5.95 |
| Diced Beef Casserole 500g | 11.00 |
| Pork Rashers Medium | 10.96 |
| Woolworths Lamb Extra Trim Cutlets | 27.51 |
| WW Extra Virgin Olive Oil Spray 150g | 3.70 |
| Asparagus Mini | 3.50 |
| Bakery Du Jour Brioche Loaf 450g | 4.50 |
| Blueberry 170g | 2.00 |
| Berry Strawberry Premium 300g | 4.50 |
.
ensure to always respond concisely using british english and put the processed record in a table in artefact
never accumulate records, whenever i send a new message, create a new table
.
.
.
For image-based shopping records, follow these standardisation rules:

1. Text Case Handling:
- Convert common words (e.g., "NOODLE", "SAUCE") to Title Case
- Keep abbreviated brand names (e.g., "TWF", "LKK") in their original case
- Ignore Chinese characters and question marks

2. Quantity and Unit Standardisation:
- Convert "xPk" format to "xx x1pk" (e.g., "6Pk" → "x6 x1pk")
- Convert "xPKS" format to "xx x1pk" (e.g., "5PKS" → "x5 x1pk")
- Convert weight-pack combinations to standard format (e.g., "3GX5PKS" → "3g x5 x1pk")
- Convert all bag units to pack format (e.g., "1BAGS" → "x1pk")
- For non-pack quantities, use "x" prefix (e.g., "x3")
- Keep weight units (g, kg) as is
- Remove spaces between numbers and units

3. Special Character Handling:
- If record starts with `**` (ensure double not single star) AND the text "DISCOUNT" is visible anywhere in the image, move `**` to the end of `Note`
- If record starts with `**` but NO "DISCOUNT" text is visible in the image, remove the `**` entirely
- Remove all other special characters (*, ^, #, etc.)

4. Duplicate Handling:
- Combine duplicate entries into a single line
- Sum their amounts
- Update pack quantity accordingly (e.g., two "x5 x1pk" → "x5 x2pk")

5. Output Format:
- Create table in markdown format
- Use two columns: "Note" and "Amount"
- Maintain original price in Amount column
- For duplicate items, sum the amounts

Example input:
```
**TWF NOODLE 5PKS 蛋黃拌面 6.99
*DRIED SHAVED TUNA 3GX5PKS 鰹魚碎 3.95
**GARLIC 1BAGS 有衣蒜頭 3.28
```

Example output:
| Note | Amount |
|------|---------|
| TWF Noodle x5 x1pk ** | 6.99 |
| Dried Shaved Tuna 3g x5 x1pk | 3.95 |
| Garlic x1pk ** | 3.28 |