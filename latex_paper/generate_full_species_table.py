#!/usr/bin/env python3
"""
Generate full 82-species LaTeX table for the paper
"""

species_data = """Graylag Goose,2871
Pink-footed Goose,189
Great Snipe,189
Hooded Crow,87
Carrion Crow,84
Greater White-fronted Goose,71
Common Crane,70
Common Grasshopper-Warbler,59
Eurasian Woodcock,57
Canada Goose,47
Rook,45
Mallard,27
Yellowhammer,24
Tawny Owl,23
Lesser Spotted Woodpecker,14
Eurasian Coot,14
Northern Lapwing,13
European Greenfinch,11
Ring-necked Pheasant,10
Eurasian Curlew,10
Gray Heron,9
Meadow Pipit,9
Red-breasted Flycatcher,9
Eurasian Nutcracker,9
Little Bunting,9
Mistle Thrush,7
Tundra Swan,7
White Wagtail,7
Water Rail,7
Eurasian Magpie,6
Gray Wagtail,6
Black-headed Gull,6
European Robin,6
Tundra Bean-Goose,4
Arctic Warbler,4
Bank Swallow,4
European Storm-Petrel,4
Common Redpoll,4
Eurasian Pygmy-Owl,4
Western Yellow Wagtail,4
Redwing,4
Manx Shearwater,3
Gray Partridge,3
Whooper Swan,3
Snow Bunting,3
Lapland Longspur,3
Reed Bunting,2
Taiga Bean-Goose,2
Ortolan Bunting,2
Red-throated Loon,2
Tree Pipit,2
Gadwall,2
Herring Gull,2
Eurasian Blue Tit,2
Black Woodpecker,2
Common Sandpiper,2
Dunlin,2
Common Snipe,2
Eurasian Oystercatcher,2
Eurasian Jay,1
Common House-Martin,1
Bar-headed Goose,1
Fieldfare,1
Black-bellied Plover,1
Western Capercaillie,1
Black-legged Kittiwake,1
Brambling,1
Brant,1
Common Buzzard,1
Common Goldeneye,1
Common Raven,1
Eurasian Eagle-Owl,1
European Golden-Plover,1
River Warbler,1
Great Gray Shrike,1
Richard's Pipit,1
Common Tern,1
Corn Crake,1
Dunnock,1
Eurasian Moorhen,1
Pine Grosbeak,1
Arctic Tern,1"""

lines = species_data.strip().split('\n')
print("Total species:", len(lines))

# Split into 3 columns for better page layout
col1 = lines[0:28]
col2 = lines[28:56]
col3 = lines[56:82]

print("\n% LaTeX table code (3 columns, compact format)\n")
print("\\begin{table}[H]")
print("\\centering")
print("\\caption{Complete verified species list (82 species)}")
print("\\label{tab:species_full}")
print("\\tiny")
print("\\begin{tabular}{lr|lr|lr}")
print("\\toprule")
print("\\textbf{Species} & \\textbf{N} & \\textbf{Species} & \\textbf{N} & \\textbf{Species} & \\textbf{N} \\\\")
print("\\midrule")

max_rows = max(len(col1), len(col2), len(col3))
for i in range(max_rows):
    row = []
    for col in [col1, col2, col3]:
        if i < len(col):
            name, count = col[i].rsplit(',', 1)
            row.append(f"{name} & {count}")
        else:
            row.append(" & ")
    print(" & ".join(row) + " \\\\")

print("\\bottomrule")
print("\\end{tabular}")
print("\\end{table}")
