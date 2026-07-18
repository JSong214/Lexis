import { useMutation } from '@tanstack/react-query'

import { apiPost } from '../../lib/api-client'

export type CefrLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
export type ContentMode = 'explanatory_scenario' | 'micro_case' | 'comparison'
export type WordRole = 'anchor' | 'support' | 'deferred' | 'excluded'

export interface WordSense {
  id: string
  definition: string
  meaningZh: string
  partOfSpeech: string
  collocations: string[]
  register: string
  semanticDomains: string[]
}

export interface WordSemanticProfile {
  word: string
  lemma: string
  difficulty: string
  senses: WordSense[]
  sourceName: string
  sourceVersion: string
}

export interface KnowledgeSource {
  id: string
  title: string
  publisher: string
  url: string
  version: string
}

export interface TopicWordUsage {
  word: string
  role: WordRole
  senseId: string | null
  meaningZh: string | null
  partOfSpeech: string | null
  topicRole: string | null
  relationType: string | null
}

export interface RelationEvidence {
  word: string
  senseId: string
  topicRole: string
  relationType: string
  explanation: string
}

export interface TopicProposal {
  id: string
  topicId: string
  title: string
  coreQuestion: string
  coreKnowledge: string
  contentMode: ContentMode
  wordUsages: TopicWordUsage[]
  relationEvidence: RelationEvidence[]
  deferredWords: string[]
  excludedWords: string[]
  relationExplanation: string
  rationale: string
}

export interface TopicProposalResult {
  snapshotId: string
  profiles: WordSemanticProfile[]
  proposals: TopicProposal[]
  unmatchedWords: string[]
  planningMode: 'curated' | 'language_fallback'
  notice: string | null
}

interface TopicProposalInput {
  cefrLevel: CefrLevel
  examGoal: string
  selectedWords: string[]
}

export function useTopicProposalsMutation() {
  return useMutation({
    mutationFn: (input: TopicProposalInput) => apiPost<TopicProposalResult>(
      '/lessons/topic-proposals',
      input,
    ),
  })
}
