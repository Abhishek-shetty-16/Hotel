# Task: Fix Git line ending warnings

## Steps:
- [x] Create .gitignore with standard Python/Flask/Django ignores
- [x] Create .gitattributes to normalize line endings (LF in repo)
- [ ] Refresh Git index: `git rm --cached -r . && git reset HEAD .`
- [ ] `git add . && git status` to verify no warnings
- [ ] Commit: `git add .gitattributes && git commit -m "Add .gitattributes to fix line ending warnings"`

## Next Steps:
- Test git add after index refresh to confirm warnings gone.
