set terminal x11


plot "proposedHMM.txt" u 2:3 index 0, "proposedHMM.txt" u 2:3 index 1, "proposedHMM.txt" u 2:3 index 2, "proposedHMM.txt" u 2:3 index 3, "hiddenMCMC2.txt" u 2:3 w p pt 2 ps 4 lw 5 lc -1

