if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")

    from demo.demo import demo

    demo()


from q2gui import q2model

class Q2Model(q2model.Q2Model):
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()
        return super().refresh()
