import { CheckCircle } from '@phosphor-icons/react'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { Card, PrimaryButton, ProgressBar, SectionHeading, StatusChip, WordChip } from '../components/ui'

const steps = ['Reading', 'Vocabulary aid', 'Grammar lens', 'Exercises']
const exercises = [
  { title: 'Vocabulary context', prompt: 'Which phrase best preserves the meaning of “stable anchor”?', options: ['A fixed reference point', 'A rough first draft', 'An ambiguous estimate'] },
  { title: 'Grammar lens', prompt: 'Choose the sentence that correctly uses “while” to contrast two ideas.', options: ['While estimates vary, the anchor stays stable.', 'While the anchor stable, estimates vary.', 'Estimates while vary the anchor.'] },
  { title: 'Logic check', prompt: 'What is the author’s main reason for using an anchor?', options: ['To reduce random variation', 'To avoid all estimates', 'To increase the word count'] },
]

export function LessonPage() {
  const navigate = useNavigate()
  const [activeStep, setActiveStep] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const currentExercise = exercises[Math.min(activeStep - 1, exercises.length - 1)]

  function continueLesson() {
    if (activeStep < steps.length - 1) setActiveStep((value) => value + 1)
    else navigate('/app/lessons/demo/complete')
  }

  return (
    <div className="pt-1">
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-[-0.025em]">Estimating with stable anchors</h1>
          <p className="mt-1 text-xs text-ink-muted">B2 · IELTS reading · 12 focus words</p>
        </div>
        <StatusChip>Lesson active</StatusChip>
      </div>

      <div className="mt-3"><ProgressBar value={(activeStep + 1) * 25} /></div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.9fr)]">
        <Card className="p-5 md:p-7">
          <div className="flex items-start justify-between gap-4">
            <SectionHeading subtitle="Read for meaning before opening the learning aids.">Context reading</SectionHeading>
            <span className="rounded-md bg-surface-muted px-2 py-1 text-[11px] text-ink-muted">Part 1 of 4</span>
          </div>

          <article className="mt-5 rounded-lg border border-[#e7e2d7] bg-[#fffdf8] p-5 md:p-7">
            <h2 className="text-2xl font-semibold tracking-[-0.025em]">A Better Way to Estimate</h2>
            <p className="mt-2 text-sm leading-6 text-ink-muted">How stable reference points make uncertain decisions more reliable.</p>
            <div className="mt-5 space-y-4 text-[15px] leading-7 text-[#34393d]">
              <p>When a team must estimate an uncertain outcome, the first number often shapes every discussion that follows. A stable anchor can help, but only when everyone understands what the reference point represents.</p>
              <p>Good estimators compare the new situation with a familiar segment, state the criteria they are using, and then adjust the draft estimate. This process does not remove uncertainty. It makes the reasoning visible and easier to validate.</p>
              <p>An anchor becomes misleading when it is treated as a final answer. The useful habit is to retain the structure while remaining willing to revise the number as new context appears.</p>
            </div>
          </article>

          <div className="mt-5">
            <SectionHeading subtitle="Tap words to mark them for review.">Focus vocabulary</SectionHeading>
            <div className="mt-3 flex flex-wrap gap-2">{['anchor', 'segment', 'estimate', 'criteria', 'retain', 'validate'].map((word) => <WordChip key={word}>{word}</WordChip>)}</div>
          </div>
        </Card>

        <div className="grid content-start gap-4">
          <Card className="p-4">
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-2">
              {steps.map((step, index) => (
                <button className={`rounded-lg px-3 py-2 text-left text-xs font-medium transition ${activeStep === index ? 'bg-lexis-soft text-lexis' : 'bg-surface-muted text-ink-muted'}`} key={step} onClick={() => setActiveStep(index)} type="button">
                  <span className="mr-2">{index + 1}.</span>{step}
                </button>
              ))}
            </div>
          </Card>

          {activeStep === 0 && (
            <Card className="p-5">
              <SectionHeading subtitle="Complete the reading before using the aids.">Reading check</SectionHeading>
              <div className="mt-4 flex items-center gap-2 text-sm text-lexis"><CheckCircle size={20} /> Reading is ready</div>
            </Card>
          )}

          {activeStep === 1 && (
            <Card className="p-5">
              <SectionHeading subtitle="Short explanations tied to this article.">Vocabulary aid</SectionHeading>
              <dl className="mt-4 space-y-4 text-sm">
                <div><dt className="font-semibold">anchor</dt><dd className="mt-1 text-ink-muted">a stable reference used to compare a new estimate</dd></div>
                <div><dt className="font-semibold">retain</dt><dd className="mt-1 text-ink-muted">to keep an important quality or structure</dd></div>
              </dl>
            </Card>
          )}

          {activeStep === 2 && (
            <Card className="p-5">
              <SectionHeading subtitle="One useful structure from the reading.">Grammar lens</SectionHeading>
              <p className="mt-4 rounded-lg bg-surface-muted p-4 text-sm leading-6"><strong>while + clause</strong> introduces a contrast: “The anchor stays stable while the estimate changes.”</p>
            </Card>
          )}

          {activeStep === 3 && (
            <Card className="p-5">
              <SectionHeading subtitle="Your answer is stored with this attempt.">{currentExercise.title}</SectionHeading>
              <p className="mt-4 text-sm leading-6">{currentExercise.prompt}</p>
              <div className="mt-4 grid gap-2">
                {currentExercise.options.map((option) => (
                  <button className={`rounded-lg border p-3 text-left text-sm transition ${answers[0] === option ? 'border-lexis bg-lexis-soft text-lexis' : 'border-line hover:bg-surface-muted'}`} key={option} onClick={() => setAnswers({ 0: option })} type="button">{option}</button>
                ))}
              </div>
            </Card>
          )}

          <PrimaryButton className="w-full" disabled={activeStep === 3 && !answers[0]} onClick={continueLesson}>
            {activeStep === steps.length - 1 ? 'Submit and view summary' : `Continue to ${steps[activeStep + 1]}`}
          </PrimaryButton>
        </div>
      </div>
    </div>
  )
}
