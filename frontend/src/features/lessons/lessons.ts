import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiGet, apiPost } from '../../lib/api-client'

export interface WordAid {
  meaningZh: string
  word: string
}

export interface Exercise {
  type: 'vocabulary_context' | 'syntax' | 'paragraph_logic' | 'output'
  question: string
  options: string[]
}

export interface ContextLesson {
  id: string
  snapshotId: string
  provider: string
  status: string
  cefrLevel: 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
  examGoal: string
  content: {
    title: string
    readingText: string
    unfamiliarWords: WordAid[]
    targetWords: string[]
    grammarAnalysis: string[]
    exercises: Exercise[]
  }
  validationErrors: string[]
  generationMetadata: Record<string, unknown>
  createdAt: string
}

export interface ExerciseFeedback {
  id: string
  attemptId: string
  exerciseIndex: number
  exerciseType: Exercise['type']
  answer: string
  isCorrect: boolean
  feedbackText: string
  updatedAt: string
}

export interface LessonAttempt {
  id: string
  lessonId: string
  status: string
  finalSummary: string | null
  feedback: ExerciseFeedback[]
  createdAt: string
  updatedAt: string
}

export interface MasteryUpdate {
  word: string
  status: string
  exposureCount: number
  successfulAttempts: number
}

export interface LessonCompletion {
  attempt: LessonAttempt
  masteryUpdates: MasteryUpdate[]
}

export interface LessonHistoryItem {
  id: string
  title: string
  cefrLevel: ContextLesson['cefrLevel']
  attemptStatus: string | null
  answeredCount: number
  correctCount: number
  exerciseCount: number
  createdAt: string
  completedAt: string | null
}

interface GenerateLessonInput {
  cefrLevel: ContextLesson['cefrLevel']
  examGoal: string
  selectedWords: string[]
}

interface SubmitAnswerInput {
  exerciseIndex: number
  answer: string
}

export function useGenerateLessonMutation() {
  return useMutation({
    mutationFn: (input: GenerateLessonInput) => apiPost<ContextLesson>(
      '/lessons/generate',
      input,
    ),
  })
}

export function useLessonQuery(lessonId: string | undefined) {
  return useQuery({
    queryKey: ['lessons', lessonId],
    queryFn: () => apiGet<ContextLesson>('/lessons/' + lessonId),
    enabled: Boolean(lessonId),
    retry: false,
  })
}

export function useLessonAttemptQuery(lessonId: string | undefined) {
  return useQuery({
    queryKey: ['lesson-attempt', lessonId],
    queryFn: () => apiGet<LessonAttempt | null>('/lessons/' + lessonId + '/attempt'),
    enabled: Boolean(lessonId),
    retry: false,
  })
}

export function useSubmitAnswerMutation(lessonId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: SubmitAnswerInput) => apiPost<ExerciseFeedback>(
      '/lessons/' + lessonId + '/answers',
      input,
    ),
    onSuccess: () => queryClient.invalidateQueries({
      queryKey: ['lesson-attempt', lessonId],
    }),
  })
}

export function useCompleteLessonMutation(lessonId: string | undefined) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => apiPost<LessonCompletion>('/lessons/' + lessonId + '/complete'),
    onSuccess: (completion) => {
      queryClient.setQueryData(['lesson-completion', lessonId], completion)
      queryClient.setQueryData(['lesson-attempt', lessonId], completion.attempt)
    },
  })
}

export function useLessonCompletionQuery(lessonId: string | undefined) {
  return useQuery({
    queryKey: ['lesson-completion', lessonId],
    queryFn: () => apiGet<LessonCompletion>('/lessons/' + lessonId + '/completion'),
    enabled: Boolean(lessonId),
    retry: false,
  })
}

export function useLessonHistoryQuery() {
  return useQuery({
    queryKey: ['lesson-history'],
    queryFn: () => apiGet<LessonHistoryItem[]>('/lessons'),
    retry: false,
  })
}
