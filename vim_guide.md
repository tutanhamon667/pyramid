# Vim Mini Guide

| Basic Commands | Description |
|---------------|-------------|
| **Navigation** || 
| `h` | Move left |
| `j` | Move down |
| `k` | Move up |
| `l` | Move right |
| `w` | Jump to start of next word |
| `b` | Jump to start of previous word |
| `0` | Jump to start of line |
| `$` | Jump to end of line |
| `gg` | Go to first line of document |
| `G` | Go to last line of document |
| **Modes** || 
| `i` | Enter Insert mode (before cursor) |
| `a` | Enter Insert mode (after cursor) |
| `v` | Enter Visual mode |
| `ESC` or `Ctrl+[` | Return to Normal mode |
| `:` | Enter Command mode |

| Editing & Commands | Description |
|-------------------|-------------|
| **Basic Editing** || 
| `x` | Delete character under cursor |
| `dd` | Delete current line |
| `yy` | Copy (yank) current line |
| `p` | Paste after cursor |
| `P` | Paste before cursor |
| `u` | Undo |
| `Ctrl+r` | Redo |
| **Search and Replace** || 
| `/pattern` | Search forward for pattern |
| `?pattern` | Search backward for pattern |
| `n` | Repeat search forward |
| `N` | Repeat search backward |
| `:%s/old/new/g` | Replace all occurrences |

| File Operations | Description |
|----------------|-------------|
| **Saving and Quitting** || 
| `:w` | Save file |
| `:q` | Quit (fails if unsaved changes) |
| `:wq` or `:x` | Save and quit |
| `:q!` | Quit without saving (force quit) |
| **Window Management** || 
| `:sp` | Split window horizontally |
| `:vsp` | Split window vertically |
| `Ctrl+w` then `h/j/k/l` | Navigate between windows |

| Advanced Features | Description |
|------------------|-------------|
| **Text Objects** || 
| `ci"` | Change text inside quotes |
| `dt.` | Delete until dot |
| `>>` | Indent line |
| `<<` | Unindent line |
| `zz` | Center cursor on screen |
| **Pro Tips** || 
| `.` | Repeat last command |
| `ci{` | Change inside curly braces |
| `%` | Jump between matching brackets |
| `*` | Search for word under cursor |
| `ZZ` | Quick save and quit |

> **Remember**: Vim is all about composable commands. Learning the basic movements and operators allows you to combine them in powerful ways!
