import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
style.use("ggplot")
from sklearn import svm

class SVM:
    def train(self, dimensions, classes):
        clf = svm.SVC(kernel='linear', C=1, gamma=1)
        classes = [0 if x == 'M' else 1 for x in classes]
        X = np.array(dimensions)
        print('fitting')
        clf.fit(X, classes)

        w = clf.coef_[0]
        print(w)

        a = -w[0] / w[1]

        xx = np.linspace(0, 20)
        yy = a * xx - clf.intercept_[0] / w[1]

        h0 = plt.plot(xx, yy, 'k-', label="non weighted div")

        plt.scatter(X[:, 0], X[:, 1], c=classes)
        plt.legend()
        plt.show()

        return clf

    def classify(self, dimensions, classes, test):
        clf = self.train(dimensions, classes)

        tests = []
        tests.append(test)
        results = ['M' if x == 0 else 'F' for x in clf.predict(tests)]
        return results

    def classifyPersist(self, clf, test):
        tests = []
        tests.append(test)
        results = ['M' if x == 0 else 'F' for x in clf.predict(tests)]
        return results

