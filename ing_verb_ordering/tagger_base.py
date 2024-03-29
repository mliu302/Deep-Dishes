from ing_verb_ordering import scorer
from ing_verb_ordering import preproc
from ing_verb_ordering import clf_base
from ing_verb_ordering import bilstm
from ing_verb_ordering.constants import DEV_FILE, OFFSET, TRAIN_FILE, UNK, TEST_FILE, START_TAG, END_TAG
import operator

argmax = lambda x : max(x.items(),key=lambda y : y[1])[0]


def make_classifier_tagger(weights):
    """

    :param weights: a defaultdict of classifier weights
    :returns: a function that takes a list of words, and a list of candidate tags, and returns tags for all words
    :rtype: function

    """
    #raise NotImplementedError;

    def classify(words, all_tags):
        """This nested function should return a list of tags, computed using a classifier with the weights
        passed as arguments to make_classifier_tagger and using basefeatures for each token
        (just the token and the offset)

        :param words: list of words
        :param all_tags: all possible tags
        :returns: list of tags
        :rtype: list

        """
        listy = []
        for word in words:
            listy.append((argmax(clf_base.predict({word:1}, weights, all_tags)[1])))
        return listy

    return classify

#compute tag with most unique word types: check if needed?
def most_unique_tag(weights, alltags):
    tag_uniq_counts = {tag: len([tup[0] for tup in weights.keys() if tup[0] == tag]) for tag in alltags}
    return argmax(tag_uniq_counts)


def apply_tagger(tagger,outfilename,all_tags=None,trainfile=TRAIN_FILE,testfile=DEV_FILE):
    title, X_tst, Y_tst = preproc.load_data(testfile)

    if all_tags is None:
        all_tags = set()
        
        # this is slow
        title, X_tr, Y_tr = preproc.load_data(trainfile)
        for i in range(len(X_tr)):
            tags = Y_tr[i]
            for tag in tags:
                all_tags.add(tag)

        for i in range(len(X_tst)):
            tags = Y_tst[i]
            for tag in tags:
                all_tags.add(tag)

            
    with open(outfilename,'w') as outfile:
        for i in range(len(X_tst)):
            words = X_tst[i]
            pred_tags = tagger(words,all_tags)
            for i,tag in enumerate(pred_tags):
                outfile.write(tag+'\n')
            outfile.write('\n')


def eval_tagger(tagger, outfilename, all_tags=None, trainfile=TRAIN_FILE, testfile=DEV_FILE):
    """Calculate confusion_matrix for a given tagger

    Parameters:
    tagger -- Function mapping (words, possible_tags) to an optimal
              sequence of tags for the words
    outfilename -- Filename to write tagger predictions to
    testfile -- (optional) Filename containing true labels

    Returns:
    confusion_matrix -- dict of occurences of (true_label, pred_label)
    """
    apply_tagger(tagger,outfilename,all_tags,trainfile,testfile)
    return scorer.get_confusion(testfile,outfilename) #run the scorer on the prediction file


def apply_model(model,outfilename,word_to_ix, all_tags=None,trainfile=TRAIN_FILE,testfile=DEV_FILE):
    """
    applies the model on the data and writes the best sequence of tags to the outfile
    """
    title, X, Y = preproc.load_data(testfile)
    if all_tags is None:
        all_tags = set()
        # this is slow
        for i in range(len(X)):
            tags = Y[i]
            for tag in tags:
                all_tags.add(tag)
            
    with open(outfilename,'w') as outfile:
        for i in range(len(X)):
            words = X[i]
            tags = Y[i]
            seq_words = bilstm.prepare_sequence(words, word_to_ix)
            pred_tags = model.predict(seq_words)
            for i,tag in enumerate(pred_tags):
                outfile.write(tag+'\n')
            outfile.write('\n')


def eval_model(model,outfilename, word_to_ix, all_tags=None,trainfile=TRAIN_FILE,testfile=DEV_FILE):
    """Calculate confusion_matrix for a given model

    Parameters:
    tagger -- Model mapping (words) to an optimal
              sequence of tags for the words
    outfilename -- Filename to write tagger predictions to
    testfile -- (optional) Filename containing true labels

    Returns:
    confusion_matrix -- dict of occurences of (true_label, pred_label)
    """
    apply_model(model,outfilename,word_to_ix, all_tags,trainfile,testfile)
    return scorer.get_confusion(testfile,outfilename) #run the scorer on the prediction file

if __name__ == '__main__':

    all_tags = preproc.get_all_tags(TRAIN_FILE)
    all_tags_dev = preproc.get_all_tags(DEV_FILE)
    all_tags_tst = preproc.get_all_tags(TEST_FILE)

    all_tags = all_tags.union(all_tags_dev)
    all_tags = all_tags.union(all_tags_tst)
    all_tags.add(START_TAG)
    all_tags.add(END_TAG)

    add_tagger = lambda words, alltags: ['add' for word in words]

    confusion = eval_tagger(add_tagger, 'add.preds', all_tags=all_tags)
    print(scorer.accuracy(confusion))