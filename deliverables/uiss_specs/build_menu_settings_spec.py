"""Spec for X15_UISS_Screen_MenuSettings.xlsx (UISS-Screen, admin panel to show / hide sidebar menus)."""
import json, sys
from asn_common import btn, header, it, out, revisions

IMG = 'deliverables/uiss_screens/asn_crossdock'
B = ["Show (check box)", "Show all (group)", "Hide all (group)", "Show all"]
T = 'TB_M_MENU_VISIBILITY'

COLS = [
    ["ROLE_CD", "VARCHAR(TBD)", "Y", "N", "Role the setting applies to (TBD: per role or global)"],
    ["MENU_GROUP", "VARCHAR(50)", "", "N", "Sidebar group, e.g. ASN, Common"],
    ["MENU_ITEM", "VARCHAR(100)", "Y", "N", "Sidebar menu, e.g. Case Consolidation Simulation"],
    ["SHOW_FLAG", "VARCHAR(1)", "", "N", "'Y' shown / 'N' hidden"],
    ["CREATED_BY", "VARCHAR(TBD)", "", "N", "User who created the record"],
    ["CREATED_DT", "DATETIME", "", "N", "Created date and time"],
    ["CHANGED_BY", "VARCHAR(TBD)", "", "N", "User who last changed the record"],
    ["CHANGED_DT", "DATETIME", "", "N", "Last changed date and time"]]


def modes(on):
    return {b: ("E" if b in on else "D") for b in B}


spec = {
 "doc_type": "screen",
 "header": header("X15", "Screen", "Menu Settings", '15-Oct-26'),
 "revisions": revisions('15-Oct-26'),
 "general": {
  "objective": ["To let the admin choose which menus are shown in the sidebar.", "Changes apply at once; Menu Settings itself is always shown so hidden menus can be shown again."],
  "display_order": [{"section": "Menu groups", "fields": [{"field": "Sidebar order of groups and menus", "order": "-"}]}],
  "buttons": [
   {"name": "Show (check box)", "function": "Show (ticked) or hide (unticked) one menu."},
   {"name": "Show all (group)", "function": "Show every menu of the group."},
   {"name": "Hide all (group)", "function": "Hide every menu of the group (except Menu Settings)."},
   {"name": "Show all", "function": "Show every menu of the sidebar."}],
  "screen_modes": [
   {"mode": "Initial Mode", "sections": [
     {"section": "Header", "description": "'{n} of {m} menus shown'", "buttons": modes(["Show all"])},
     {"section": "Menu groups", "description": "One card per sidebar group with its menus", "buttons": modes(["Show (check box)", "Show all (group)", "Hide all (group)"])}]}],
  "screen_mode_remarks": ["1) The check box of Menu Settings is disabled ('always shown').", "2) [Show all] is disabled when no menu is hidden."]
 },
 "screen_flow": [{"title": "Screen Flow - Menu Settings", "flow": {"direction": "LR", "nodes": [
     {"id": "m", "label": "Menu Settings", "type": "screen"}, {"id": "s", "label": "Sidebar (all screens)", "type": "screen"}],
    "edges": [{"from": "m", "to": "s", "label": "show / hide at once"}]}}],
 "screen_layout": [{"caption": "1. Menu Settings: two menus hidden", "image": f"{IMG}/c_15_menu_settings.png"}],
 "items": [
  {"group": "<Header>"},
  out("Counter", "Computed", "-", "Char", "-", "Label", "Right", "-", "'{n} of {m} menus shown'."),
  btn("Show all", "Shows every menu; disabled when none is hidden."),
  {"group": "<Menu Group Card (one per sidebar group)>"},
  out("Group name / count", T, "MENU_GROUP", "Char", "50", "Label", "Left", "-", "Group name and '{shown}/{total}'."),
  btn("Show all (group)", "Shows the menus of the group."), btn("Hide all (group)", "Hides the menus of the group except Menu Settings."),
  it("Show (check box)", T, "SHOW_FLAG", "Char", "1", "I", "CheckBox", "Center", "From the setting", "N", "-", "Menu Settings always ticked (disabled)", "Ticked = shown in the sidebar."),
  out("Menu name", T, "MENU_ITEM", "Char", "100", "Label", "Left", "-", "Greyed when hidden; note 'always shown' for Menu Settings, 'existing menu' for menus not built in this project.")],
 "data_map": {"blocks": [
  {"source": "Key-in from screen", "destination": {"table": T, "operation": "Update", "description": "Check box / Show all / Hide all",
                                                 "keys": [{"field": "ROLE_CD + MENU_ITEM", "value": "Menu of the action"}]},
   "mappings": [{"dest_field": "SHOW_FLAG", "description": "'Y' when ticked / Show all; 'N' when unticked / Hide all"},
                {"dest_field": "ROLE_CD", "description": "Not changed"}, {"dest_field": "MENU_GROUP", "description": "Not changed"},
                {"dest_field": "MENU_ITEM", "description": "Not changed"}, {"dest_field": "CREATED_BY", "description": "Not changed"},
                {"dest_field": "CREATED_DT", "description": "Not changed"},
                {"dest_field": "CHANGED_BY", "description": "Login user ID"}, {"dest_field": "CHANGED_DT", "description": "Server system date-time"}]}]},
 "operation": [
  {"type": "heading", "text": "5.1 Show / Hide"},
  {"type": "bullets", "marker": "a.", "level": 2, "items": [
    "The screen lists every sidebar group as a card with its menus and a check box per menu (ticked = shown).",
    "Ticking / unticking a menu, [Show all] / [Hide all] of a group and [Show all] of the header save at once and the sidebar is redrawn; there is no Save button.",
    "A group whose menus are all hidden is not shown in the sidebar.",
    "Menu Settings can never be hidden."]},
  {"type": "heading", "text": "5.2 Notes"},
  {"type": "bullets", "marker": "-", "level": 2, "items": [
    "Prototype: the setting is kept in the browser. In Supplier System it is saved in TB_M_MENU_VISIBILITY (proposed); per role or global is TBD.",
    "Access to this screen: admin only (TBD)."]}],
 "display_messages": [],
 "logging_messages": [],
 "tables": [{"name": T, "kind": "master", "proposed": True, "description": "Sidebar menu visibility. Name and columns proposed.", "columns": COLS}]
}
json.dump(spec, open(sys.argv[1], 'w'), indent=1)
