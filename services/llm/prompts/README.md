# Prompt Templates

P0 keeps prompt definitions as explicit contracts even when the default provider is mock/heuristic.

## profile_extract_facts

Input: resume/project text, target roles.

Output schema: CareerFact list, SkillEvidence candidates, missing info, needs confirmation flags.

## project_create_card

Input: project README/text, target role, source refs.

Output schema: TechProject fields, resume bullets, interview questions, improvement suggestions.

## job_parse_jd

Input: JD text and optional source URL.

Output schema: Job title/company, must-have, nice-to-have, responsibilities, tech stack, seniority guess.

## application_create_package

Input: Job, CareerFact, SkillEvidence, TechProject.

Output schema: resume Markdown, project description, recruiter message, source fact refs, questions to confirm.

## interview_prepare

Input: Job, application package, project cards.

Output schema: focus areas, questions, reverse questions, story card inputs.

## realtime_generate_hint

Input: current question, job context, project/story cards, hint level.

Output schema: recommended project/story, answer structure, safety reminder, source refs.

