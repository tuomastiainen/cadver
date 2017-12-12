drawing_setup_file $PRO_DIRECTORY\text\prodetail.dtl
format_setup_file $PRO_DIRECTORY\text\prodetail.dtl
pro_unit_length unit_inch
pro_unit_mass unit_pound
template_designasm $PRO_DIRECTORY\templates\inlbs_asm_design.asm
template_new_ecadasm $PRO_DIRECTORY\templates\inlbs_ecad_asm.asm
template_drawing $PRO_DIRECTORY\templates\c_drawing.drw
template_sheetmetalpart $PRO_DIRECTORY\templates\inlbs_part_sheetmetal.prt
template_solidpart $PRO_DIRECTORY\templates\inlbs_part_solid.prt
template_boardpart $PRO_DIRECTORY\templates\inlbs_ecad_board.prt
todays_date_note_format %Mmm-%dd-%yy
tolerance_standard ansi
weld_ui_standard ansi
search_path_file $CREO_COMMON_FILES\afx\parts\prolibrary\search.pro
last_session_directory_path C:\cadver
mass_property_calculate automatic
regen_failure_handling resolve_mode

