#!/bin/zsh

cd '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe'

git diff --quiet && git diff --cached --quiet || { echo "Uncommitted changes detected. Commit or stash them first."; exit 1; }

git mv 'dissertation/MGTK751_A1-3_00.md' 'dissertation/MGTK751_A1-3.md'
git mv 'dissertation/MGTK751_A1R_00.md' 'dissertation/MGTK751_A1R.md'
git mv 'dissertation/MGTK751_A1_00.md' 'dissertation/MGTK751_A1.md'
git mv 'dissertation/MGTK751_A1_Template_00.md' 'dissertation/MGTK751_A1_Template.md'
git mv 'dissertation/MGTK751_A1_grade_00.md' 'dissertation/MGTK751_A1_grade.md'
git mv 'dissertation/MGTK751_A1_overview_00.md' 'dissertation/MGTK751_A1_overview.md'
git mv 'dissertation/MGTK751_A1_temp_00.md' 'dissertation/MGTK751_A1_temp.md'
git mv 'dissertation/MGTK751_A1_temp_feedback_00.md' 'dissertation/MGTK751_A1_temp_feedback.md'
git mv 'dissertation/MGTK751_A3_Template_00.md' 'dissertation/MGTK751_A3_Template.md'
git mv 'dissertation/MGTK751_Concept_Brief_comp_00.md' 'dissertation/MGTK751_Concept_Brief_comp.md'
git mv 'dissertation/MGTK751_CoreRef_00.md' 'dissertation/MGTK751_CoreRef.md'
git mv 'dissertation/MGTK751_DevPlan_00.md' 'dissertation/MGTK751_DevPlan.md'
git mv 'dissertation/MGTK751_Lectures_index_00.md' 'dissertation/MGTK751_Lectures_index.md'
git mv 'dissertation/MGTK751_Meetings_distilled_00.md' 'dissertation/MGTK751_Meetings_distilled.md'
git mv 'dissertation/MGTK751_Official_Files_distilled_00.md' 'dissertation/MGTK751_Official_Files_distilled.md'
git mv 'dissertation/MGTK751_Official_Files_full_00.md' 'dissertation/MGTK751_Official_Files_full.md'
git mv 'dissertation/MGTK751_Potential_Advisors_00.md' 'dissertation/MGTK751_Potential_Advisors.md'
git mv 'dissertation/MGTK751_ProjectSummary_00.md' 'dissertation/MGTK751_ProjectSummary.md'
git mv 'dissertation/MGTK751_RefRepo_00.md' 'dissertation/MGTK751_RefRepo.md'
git mv 'dissertation/MGTK751_Seminars_distilled_00.md' 'dissertation/MGTK751_Seminars_distilled.md'
git mv 'dissertation/lu_00.md' 'dissertation/lu.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_Preamble_00.md' 'dissertation/Lectures/MGTK751_Lectures_Preamble.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W1_00.md' 'dissertation/Lectures/MGTK751_Lectures_W1.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W1_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W1_distilled.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W2_00.md' 'dissertation/Lectures/MGTK751_Lectures_W2.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W2_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W2_distilled.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W3_00.md' 'dissertation/Lectures/MGTK751_Lectures_W3.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W3_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W3_distilled.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W4_00.md' 'dissertation/Lectures/MGTK751_Lectures_W4.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W4_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W4_distilled.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W5_00.md' 'dissertation/Lectures/MGTK751_Lectures_W5.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W5_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W5_distilled.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W6_00.md' 'dissertation/Lectures/MGTK751_Lectures_W6.md'
git mv 'dissertation/Lectures/MGTK751_Lectures_W6_distilled_00.md' 'dissertation/Lectures/MGTK751_Lectures_W6_distilled.md'

git commit -m "Batch remove _00 suffix from dissertation files"

git push origin main
