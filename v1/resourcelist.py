import logging
from property import Property,BoolProperty

resourcelists = {}

def registerList(name, resourcelist):
    resourcelists[name] = resourcelist
def getListByName(name):
    return resourcelists.get(name)

class ResourceList(object):
    
    def __init__(self, data, startIndex=0):
        self.data = data
        self.index = Property(startIndex, int)
        self.isInitialIndex = True
        
    def isInRange(self, index):
        return index>=0 and index<len(self.data)
        
    def select(self, mode, value):
        if mode == "absolute":
            return self.selectAbsolute(value)
        elif mode == "relative":
            return self.selectRelative(value)
        elif mode == "scale":
            return self.selectByScale(value)
        
    def selectAbsolute(self, index):
        if self.isInRange(index):
            isInitialIndex = False
            self.index.setValue(index)
            return index
        else:
            logging.warning("ResourceList: Could not select resource list index {0}, out of range!".format(index)) 
            
    def selectRelative(self, relativeChange):
        if isInitialIndex:
            if relativeChange > 0:
                relativeChange -= 1
            self.isInitialIndex = False
        newIndex = (self.index + relativeChange) % len(self.data)
        self.index.setValue(newIndex)
        return newIndex
        
    def selectByScale(self, percentage):
        if percentage >= 0 and percentage <= 1:
            self.isInitialIndex = False
            newIndex = min(len(self.data)*percentage, len(self.data)-1)
            self.index.setValue(newIndex)
            return newIndex
        else:
            logging.warning("ResourceList: selectByScale only accepts values in the range 0 <= x <= 1, {0} supplied".format(percentage))
            
    def getSelectedData(self):
        return self.data[self.index]
        
    def size(self):
        return len(data)
        
    def isSelected(self, index):
        return index == self.index
        
class MultiChoiceResourceList(ResourceList):
    
    def __init__(self, data, selected=[], eventsDir=BoolProperty.BOTH):
        ResourceList.__init__(self, data)
        self.data = data
        self.selected = []
        counter = 0
        for entry in data:
            self.selected.append(BoolProperty(counter in selected, eventsDir))
            counter += 1
            
    def select(self, mode, value):
        if mode == "toggle":
            return self.toggleSelect(value)
        elif mode == "unselect":
            return self.unselect(value)
        else:
            return super(MultiChoiceResourceList, self).select(mode, value)
            
    def toggleSelect(self, index):
        if self.isInRange(index):
            return self.doSelect(index, not self.selected[index].getValue())
            
    def unselect(self, index):
        self.doSelect(index, False)
            
    def selectAbsolute(self, index):
        return self.doSelect(index)
        
    def selectRelative(self, relativeChange):
        selections = self.getSelectionIndexes()
        for index in range(0, self.size()):
            self.unselect(index)
        if relativeChange < 0:
            return self.doSelect(((selections[0] if len(selections)>0 else len(self.data))+relativeChange)%len(self.data))
        elif relativeChange > 0:
            return self.doSelect(((selections[-1] if len(selections)>0 else -1)+relativeChange)%len(self.data))
            
    def selectByScale(self, percentage):
        if percentage >= 0 and percentage <= 1:
            return self.doSelect(min(len(self.data)*percentage, len(self.data)-1))
        else:
            logging.warning("MultiChoiceResourceList: selectByScale only accepts values in the range 0 <= x <= 1, {0} supplied".format(percentage))
            
    def doSelect(self, index, value=True):
        if self.isInRange(index):
            self.selected[index].setValue(value)
            return index
        else:
            logging.warning("MultiChoiceResourceList: Invalid selection index provided : {0}".format(index))
            
    def getSelectionIndexes(self):
        return [index for index,val in enumerate(self.selected) if val.getValue()]
        
    def getSelectedData(self):
        return [self.data[index] for index in self.getSelectionIndexes()]
        
    def isSelected(self, index):
        return self.isInRange(index) and self.selected[index].getValue()
        
        
