import src
import sys
import pytest

def test_answer():
    assert 1 == 1

## PREPARE CONFIG DATA
def tags():
    t = {'tags':['1','2']}
    return t

validColumnTypes = ['boolean', 'number', 'decimal', 'date', 'datetime', 'string']
def typedefs(sourceName):
    #generate all valid types with the same column name as the type
    columns = {}
    for idx,c in enumerate(validColumnTypes):
        columns['col' + str(idx)] = {'type': c}
    print columns
    return {'typedefs':
            {sourceName: columns }}

def tagsAndTypes(sourceName):
    a = tags().copy()
    a.update(typedefs(sourceName))
    return a

## TEST INVALID CONFIG, SHOULD FAIL
@pytest.fixture(params=[typedefs('test'), tagsAndTypes('test')])
def invalidConfig(request):
    config = { 'storage' :
        { 'input':{
            'tables': [{'source':'blabla'}]
        }
      },
               'parameters':request.param
    }
    return config


def test_configInvalid(invalidConfig):
    assert src.checkConfig(invalidConfig) == False

@pytest.fixture(params=[{}, []])
def emptyInput(request):
    config = { 'storage' :
        { 'input':{
            'tables': request.param
        }
      },
    }
    return config

#test empty parameters = should pass
def test_validEmptyInput():
    config = { 'storage' :
        { 'input':{
            'tables': [{'source':'blabla'}]
        }
      },
    }
    assert src.checkConfig(config) == True

def test_emptyInput(emptyInput):
    assert src.checkConfig(emptyInput) == False

## TEST VALID CONFIG, SHOULD PASS
@pytest.fixture(params=[tags(), typedefs('test'), tagsAndTypes('test')])
def validConfig(request):
    config = { 'storage' :
        { 'input':{
            'tables': [{'source':'test'}]
        }
      },
               'parameters':request.param
    }
    return config


def test_configOK(validConfig):
    assert src.checkConfig(validConfig) == True
