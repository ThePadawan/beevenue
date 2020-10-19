from blinker import Namespace

_beevenue_signals = Namespace()

medium_deleted = _beevenue_signals.signal("medium_deleted")
medium_added = _beevenue_signals.signal("medium_added")
medium_updated = _beevenue_signals.signal("medium_updated")

alias_added = _beevenue_signals.signal("alias_added")
alias_removed = _beevenue_signals.signal("alias_removed")

implication_added = _beevenue_signals.signal("implication_added")
implication_removed = _beevenue_signals.signal("implication_removed")

tag_renamed = _beevenue_signals.signal("tag_renamed")
