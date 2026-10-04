# Related work notes for the final paper

These papers were used to shape the Checkpoint 2 evaluation design.

1. He Ye, Matias Martinez, Thomas Durieux, and Martin Monperrus. "A Comprehensive Study of Automatic Program Repair on the QuixBugs Benchmark." 2018. arXiv:1805.03454.
   - Why it matters: the study found many patches that passed available tests but were still overfitting. This supports measuring functional test success separately from simple compilation and treating a compiling patch as insufficient evidence of correctness.

2. Julian Aron Prenner and Romain Robbes. "Automatic Program Repair with OpenAI's Codex: Evaluating QuixBugs." 2021. arXiv:2111.03922.
   - Why it matters: this is a direct example of evaluating an LLM-based repair system on the QuixBugs benchmark and motivates using the same cases for the baseline and the LLM.

3. Chunqiu Steven Xia and Lingming Zhang. "Keep the Conversation Going: Fixing 162 out of 337 bugs for $0.42 each using ChatGPT." 2023. arXiv:2304.00385.
   - Why it matters: ChatRepair uses test-failure feedback during repair. Checkpoint 2 similarly supplies compiler, runtime, or failed-test context to the model instead of evaluating syntax errors only.

4. Rene Just, Darioush Jalali, and Michael D. Ernst. "Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs." ISSTA 2014, pp. 437-440.
   - Why it matters: Defects4J pairs real Java faults with tests that expose them. It remains a planned source for scaling the final project beyond the smaller Checkpoint 2 micro-benchmark suite.

## Evaluation ideas carried into this project

- Run the local rule-based baseline and the LLM on the exact same cases.
- Record patch compilation success and functional test success as different metrics.
- Include syntax, logic, and runtime bugs rather than only missing semicolons.
- Keep the exact benchmark programs and their black-box tests in the submitted artifact.
- Record response time for each repair attempt.
- Do not claim a patch is correct only because it compiles.
