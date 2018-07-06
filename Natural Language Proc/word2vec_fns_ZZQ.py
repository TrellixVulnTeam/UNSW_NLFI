import tensorflow as tf
import numpy as np
import collections

data_index = 0

def generate_batch(data, batch_size, skip_window):
    """
    Generates a mini-batch of training data for the training CBOW
    embedding model.
    :param data (numpy.ndarray(dtype=int, shape=(corpus_size,)): holds the
        training corpus, with words encoded as an integer
    :param batch_size (int): size of the batch to generate
    :param skip_window (int): number of words to both left and right that form
        the context window for the target word.
    Batch is a vector of shape (batch_size, 2*skip_window), with each entry for the batch containing all the context words, with the corresponding label being the word in the middle of the context
    """
    global data_index
    # assert batch_size % num_skips == 0
    # assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1  # [ skip_window target skip_window ]
    buffer = collections.deque(maxlen=span)
    if data_index + span > len(data):
        data_index = 0
    buffer.extend(data[data_index:data_index + span])
    data_index += span

    for i in range(batch_size):
        buffer_del = [j for j in buffer if j != buffer[skip_window]]
        if len(buffer_del) < 2*skip_window:
            pad = 2*skip_window - len(buffer_del)
            for _ in range(pad):
                buffer_del.append(0)
        # print(len(buffer))
        # buffer_del = []
        # for j in range(len(buffer)):
        #     if j != skip_window:
        #         buffer_del.append(buffer[j])
        # new_length = len(buffer_del)
        # buffer_del = [j for j in buffer if j != buffer[skip_window]]
        # if len(buffer_del) < skip_window * 2:
        #     needed_blank = (skip_window * 2) - len(buffer_del)
        #     buffer_del = buffer_del + collections.deque([0])*needed_blank

        # if len(buffer_del) < 2*skip_window:
        #     pad = 2*skip_window - len(buffer_del)
        #     for _ in range(pad):
        #         buffer_del.append(0)

        batch[i] = buffer_del
        labels[i,0] = buffer[skip_window]
        # when the indexing reaches the end of the data, you need to start again
        if data_index == len(data):
            buffer.extend(data[:span])
            data_index = span
        # make the scanning move forward with one more indexing(since the buffer.length is fixed,
        # it will kick the first element)
        else:
            buffer.append(data[data_index])
            data_index = data_index + 1

    data_index = (data_index - span) % len(data)
    return batch, labels

def get_mean_context_embeds(embeddings, train_inputs):
    """
    :param embeddings (tf.Variable(shape=(vocabulary_size, embedding_size))
    :param train_inputs (tf.placeholder(shape=(batch_size, 2*skip_window))
    returns:
        `mean_context_embeds`: the mean of the embeddings for all context words
        for each entry in the batch, should have shape (batch_size,
        embedding_size)
    """
    # cpu is recommended to avoid out of memory errors, if you don't
    # have a high capacity GPU
    with tf.device('/cpu:0'):
        embed = tf.nn.embedding_lookup(embeddings, train_inputs)
        mean_context_embeds = tf.reduce_mean(embed,1)
    return mean_context_embeds
