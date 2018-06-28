import nltk

nltk.data.path.append(r'nltk_data_folder')
import numpy
import re


class Summarizer:
    N = 100
    CLUSTER_THRESHOLD = 5
    TOP_SENTENCES = 5

    def summarize(self, text):
        summary = self.summarizeText(text)
        return summary

    def summarizeText(self, txt):
        sentences = [s for s in nltk.tokenize.sent_tokenize(txt)]
        normalizedSentences = self.stripNewLines(sentences)
        if len(normalizedSentences) == 0:
            return dict([('Success', False), ('Description', '')])
        words = [w.lower() for sentence in normalizedSentences for w in
                 nltk.tokenize.word_tokenize(sentence)]
        fdist = nltk.FreqDist(words)
        stopwords = nltk.corpus.stopwords.words('english')
        top_n_words = [w[0] for w in fdist.items()
                       if w[0] not in stopwords][:self.N]
        scoredSentences = self.scoreSentences(normalizedSentences, top_n_words)
        # Approach 1
        avg = numpy.mean([s[1] for s in scoredSentences])
        std = numpy.std([s[1] for s in scoredSentences])
        mean_scored = [(sent_idx, score) for (sent_idx, score) in scoredSentences
                       if score > avg + 0.5 * std]
        # Approach 2
        top_n_scored = sorted(
            scoredSentences, key=lambda s: s[1])[-self.TOP_SENTENCES:]
        top_n_scored = sorted(top_n_scored, key=lambda s: s[0])
        meanSummary = ''
        for (idx, score) in mean_scored:
            meanSummary += ' ' + \
                           normalizedSentences[idx][:1].capitalize(
                           ) + normalizedSentences[idx][1:]
        topNSummary = ''
        for (idx, score) in top_n_scored:
            topNSummary += ' ' + \
                           normalizedSentences[idx][:1].capitalize(
                           ) + normalizedSentences[idx][1:]
        return dict([('Success', True), ('MeanDescription', meanSummary[1:]), ('TopNDescription', topNSummary[1:])])

    def stripNewLines(self, sentences):
        normalizedSentences = []
        sentences = [s.lower() for s in sentences]
        for s in sentences:
            s = re.sub(r'[^\x00-\x7f]', r'', s)
            if '\n' in s:
                s = s.replace('\n', ' ')
                while '  ' in s:
                    s = s.replace('  ', ' ')
            if not 'page discussion view source history teams log in' in s and (
                    'loading menubar' not in s and (not re.search(r'^team:\w+', s))):
                normalizedSentences.append(s)
        return normalizedSentences

    def scoreSentences(self, sentences, important_words):
        scores = []
        sentence_idx = -1
        for s in [nltk.tokenize.word_tokenize(s) for s in sentences]:
            sentence_idx += 1
            word_idx = []
            for w in important_words:
                try:
                    word_idx.append(s.index(w))
                except ValueError:
                    pass
            word_idx.sort()
            if len(word_idx) == 0:
                continue
            clusters = []
            cluster = [word_idx[0]]
            i = 1
            while i < len(word_idx):
                if word_idx[i] - word_idx[i - 1] < self.CLUSTER_THRESHOLD:
                    cluster.append(word_idx[i])
                else:
                    clusters.append(cluster[:])
                    cluster = [word_idx[i]]
                i += 1
            clusters.append(cluster)
            max_cluster_score = 0
            for c in clusters:
                significant_words_in_cluster = len(c)
                total_words_in_cluster = c[-1] - c[0] + 1
                score = 1.0 * significant_words_in_cluster * significant_words_in_cluster / total_words_in_cluster
                if score > max_cluster_score:
                    max_cluster_score = score
            scores.append((sentence_idx, score))
        return scores
