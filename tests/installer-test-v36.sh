set -u; W=/home/claude/v36/work; P=$W/mint-pack-v36; export MINTPACK_NORESTART=1 GIT_CONFIG_GLOBAL=/root/.gitconfig; mkdir -p $W/shim; ln -sf /usr/bin/python3.12 $W/shim/python3; export PATH=$W/shim:$PATH
mk() { rm -rf $W/th; mkdir -p $W/th/.local/lib $W/th/shum; cp -a $W/fh/.local/bin $W/th/.local/; cp -a $W/base-v35 $W/th/.local/lib/zarya; cp -a $W/../src/shum/demon $W/th/shum/demon; }
snap() { (cd $W/th && find .local/lib shum/demon -path '*/.git' -prune -o -type f -print0 | sort -z | xargs -0 md5sum; git -C shum/demon rev-parse HEAD; git -C shum/demon tag | tr '\n' ' '); }
mk; export HOME=$W/th; before=$(snap)
echo "== install"; bash $P/install.sh | tail -4
echo "== reinstall"; bash $P/install.sh | tail -3
echo "== check"; xvfb-run -a bash $P/install.sh --check
echo "== uninstall"; bash $P/uninstall.sh | tail -2
after=$(snap); [ "$before" = "$after" ] && echo "UNDO BYTE-IDENTICAL (files + repo HEAD + tags)" || { echo "UNDO DIFFERS"; diff <(echo "$before") <(echo "$after") | head; }
echo "== refuse a hand-changed file"; echo '# x' >> $HOME/.local/lib/zarya/desk/03-demon-3-speech-tick-state.py; bash $P/install.sh | tail -1
mk; echo "== dirty repo"; echo x >> $HOME/shum/demon/README.md; bash $P/install.sh | grep repo; bash $P/uninstall.sh | tail -1
mk; echo "== no repo"; rm -rf $HOME/shum/demon; bash $P/install.sh | grep repo; bash $P/uninstall.sh >/dev/null; [ "$(md5sum < $HOME/.local/lib/zarya/desk/07-reactions-main.py)" = "$(md5sum < $W/base-v35/desk/07-reactions-main.py)" ] && echo "undo ok without repo"
